############
#
# Copyright (c) 2024-2026 Maxim Yudayev and KU Leuven eMedia Lab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Created 2024-2025 for the KU Leuven AidWear, AidFOG, and RevalExo projects
# by Maxim Yudayev [https://yudayev.com].
#
# ############

import time
from typing import Optional
from hermes.utils.types import LoggingSpec
import numpy as np
from vicon_dssdk import ViconDataStream

from hermes.base.nodes.producer import Producer
from hermes.utils.zmq_utils import (
    DNS_LOCALHOST,
    PORT_BACKEND,
    PORT_SYNC_HOST,
    PORT_KILL,
    PORT_VICON,
)
from hermes.utils.time_utils import get_time

from hermes.vicon.stream import ViconStream


class ViconProducer(Producer):
    """A class for streaming data from Vicon system."""

    def __init__(
        self,
        topic: str,
        host_ip: str,
        logging_spec: LoggingSpec,
        device_mapping: dict,
        sampling_rate_hz: Optional[int] = 2000,
        batch_send_rate_hz: Optional[int] = 100,
        vicon_buffer_size: Optional[int] = 1,
        buf_len: Optional[int] = 100000,
        vicon_ip: Optional[str] = DNS_LOCALHOST,
        vicon_port: Optional[str] = PORT_VICON,
        port_pub: Optional[str] = PORT_BACKEND,
        port_sync: Optional[str] = PORT_SYNC_HOST,
        port_killsig: Optional[str] = PORT_KILL,
        **_
    ):
        self._vicon_ip = vicon_ip
        self._vicon_port = vicon_port
        self._vicon_buffer_size = vicon_buffer_size

        stream_out_spec = {
            "sampling_rate_hz": sampling_rate_hz,
            "batch_send_rate_hz": batch_send_rate_hz,
            "device_mapping": device_mapping,
            "buf_len": buf_len,
        }

        super().__init__(
            topic=topic,
            host_ip=host_ip,
            stream_out_spec=stream_out_spec,
            logging_spec=logging_spec,
            sampling_rate_hz=batch_send_rate_hz,
            port_pub=port_pub,
            port_sync=port_sync,
            port_killsig=port_killsig,
        )

    @classmethod
    def create_stream(cls, stream_spec: dict) -> ViconStream:
        return ViconStream(**stream_spec)

    def _ping_device(self) -> None:
        return None

    def _connect(self) -> bool:
        self._client = ViconDataStream.Client()

        print("Connecting to Vicon", flush=True)

        while not self._client.IsConnected():
            self._client.Connect("%s:%s" % (self._vicon_ip, self._vicon_port))

        # Check setting the buffer size works.
        self._client.SetBufferSize(self._vicon_buffer_size)

        # Enable EMG data output.
        self._client.EnableDeviceData()

        # Set server push mode,
        #  server pushes frames to client buffer, TCP/IP buffer, then server buffer.
        # Code must keep up to ensure no overflow.
        self._client.SetStreamMode(ViconDataStream.Client.StreamMode.EServerPush)

        is_has_frame = False
        attempts = 50
        while not is_has_frame:
            try:
                time.sleep(1.0)
                if self._client.GetFrame():
                    is_has_frame = True
            except ViconDataStream.DataStreamException as e:
                attempts -= 1
                if attempts > 0:
                    print("Failed to get Vicon frame.", flush=True)
                    continue
                else:
                    print("Vicon frame grabbing timed out, reconnecting.", flush=True)
                    return False

        devices = self._client.GetDeviceNames()
        # Keep only EMG. This device was renamed in the Nexus SDK.
        # NOTE: When using analog connector and setting all channels as single device,
        #       _devices contains just 1 device.
        self._devices = [d for d in devices if d[0] == "EMG"]
        return True

    def _keep_samples(self) -> None:
        # NOTE: If _vicon_buffer_size == 1, the server buffers only the latest measurement -> no need to flush anything.
        pass

    # Acquire data from the sensors until signalled externally to quit
    def _process_data(self) -> None:
        try:
            # Grabbing new frame from Vicon server will raise exception once it closed.
            self._client.GetFrame()

            toa_s = get_time()
            frame_number = self._client.GetFrameNumber()
            frame_timecode = self._client.GetTimecode()

            # NOTE: New Delsys Trigno does not save sensor names and IDs persistently.
            # TODO: Test the new Vicon Datastream SDK API with HERMES>=0.4.0 batch saving functionality.
            samples = []
            for device_name, device_type in self._devices:
                device_output_details = self._client.GetDeviceOutputDetails(device_name)

                for output_name, component_name, unit in device_output_details:
                    values, occluded = self._client.GetDeviceOutputValues(
                        device_name, output_name, component_name
                    )
                    samples.append(values)

            sample_block = np.array(samples).T

            tag: str = "%s.data" % self.topic
            data = {
                "emg": sample_block,
                "timecode": np.array([frame_timecode], dtype=np.float64), 
                "counter": np.array([frame_number], dtype=np.uint32),
                "toa_s": np.zeros([sample_block.shape[0]], dtype=np.float64) + toa_s,
            }
            self._publish(
                tag=tag, process_time_s=get_time(), data={"vicon-data": data}
            )
        except ViconDataStream.DataStreamException as e:
            print(e)
        finally:
            if not self._is_continue_capture:
                # If triggered to stop and no more available data, send empty 'END' packet and join.
                self._send_end_packet()

    def _stop_new_data(self):
        # Disable all the data types
        self._client.DisableDeviceData()

    def _cleanup(self) -> None:
        # Clean up the SDK
        self._client.Disconnect()
        super()._cleanup()
