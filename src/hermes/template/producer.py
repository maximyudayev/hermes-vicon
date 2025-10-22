############
#
# Copyright (c) 2024 Maxim Yudayev and KU Leuven eMedia Lab
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

from hermes.utils.time_utils import get_time
from hermes.utils.zmq_utils import PORT_BACKEND, PORT_KILL, PORT_SYNC_HOST
from hermes.base.nodes.producer import Producer

from hermes.template import TemplateStream


class TemplateProducer(Producer):
  """A template for user extension of the Producer behavior, generating new data relayed to the Broker for consumers.
  """
  @classmethod
  def _log_source_tag(cls) -> str:
    # TODO: replace with unique modality identifier.
    return 'template-producer'


  def __init__(self,
               host_ip: str,
               logging_spec: dict,
               sampling_rate_hz: int = 1,
               port_pub: str = PORT_BACKEND,
               port_sync: str = PORT_SYNC_HOST,
               port_killsig: str = PORT_KILL,
               transmit_delay_sample_period_s: float = float('nan'),
               **_):
    # TODO: extend the function argument footprint to user-specific function.
    """Constructor of the TemplateProducer Node.

    Args:
        host_ip (str): IP address of the local master Broker.
        logging_spec (dict): Mapping of Storage object parameters to user-defined configuration values.
        sampling_rate_hz (float, optional): Expected sample rate of the device. Defaults to float('nan').
        port_pub (str, optional): Local port to publish to for local master Broker to relay. Defaults to PORT_BACKEND.
        port_sync (str, optional): Local port to listen to for local master Broker's startup coordination. Defaults to PORT_SYNC_HOST.
        port_killsig (str, optional): Local port to listen to for local master Broker's termination signal. Defaults to PORT_KILL.
        transmit_delay_sample_period_s (float, optional): Duration of the period over which to estimate propagation delay of measurements from the corresponding device. Defaults to float('nan').
    """

    # TODO: update stream specification with input arguments.
    stream_out_spec = {
      "sampling_rate_hz": sampling_rate_hz
    }

    super().__init__(host_ip=host_ip,
                     stream_out_spec=stream_out_spec,
                     logging_spec=logging_spec,
                     sampling_rate_hz=sampling_rate_hz,
                     port_pub=port_pub,
                     port_sync=port_sync,
                     port_killsig=port_killsig,
                     transmit_delay_sample_period_s=transmit_delay_sample_period_s)


  @classmethod
  def create_stream(cls, stream_spec: dict) -> TemplateStream:
    return TemplateStream(**stream_spec)


  def _ping_device(self) -> None:
    # TODO: device-specific function wrapping round-trip communication for transmission delay estimation.
    return None


  def _connect(self) -> bool:
    # TODO: 
    return True


  def _keep_samples(self) -> None:
    # TODO: start retaining streamed samples in-memory on external trigger.
    pass


  def _process_data(self) -> None:
    if self._is_continue_capture:
      ##################################
      # TODO: interface the user sensor.
      ##################################
      time.sleep(1.0)
      process_time_s: float = get_time()
      print(process_time_s, flush=True)
      ##################################
      ##################################

      tag: str = "%s.data" % self._log_source_tag()
      # TODO: match data keys to device and substream names of the Stream object.
      self._publish(tag, process_time_s=process_time_s, data={'<device-name>': {'toa': process_time_s}})
    else:
      self._send_end_packet()


  def _stop_new_data(self):
    # TODO: trigger the sensor's backend to stop generating new data.
    pass


  def _cleanup(self) -> None:
    # TODO: perform device-specific clean-up.
    super()._cleanup()
