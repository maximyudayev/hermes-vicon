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

from hermes.utils.time_utils import get_time
from hermes.utils.zmq_utils import PORT_BACKEND, PORT_FRONTEND, PORT_KILL, PORT_SYNC_HOST

from hermes.template import TemplateStream
from hermes.base.nodes.pipeline import Pipeline


class TemplatePipeline(Pipeline):
  """A template for user extension of the Pipeline behavior, consuming external data and generating new data relayed back to the Broker.
  """
  @classmethod
  def _log_source_tag(cls) -> str:
    # TODO: replace with unique modality identifier.
    return 'template-pipeline'


  def __init__(self,
               host_ip: str,
               stream_out_spec: dict,
               stream_in_specs: list[dict],
               logging_spec: dict,
               port_pub: str = PORT_BACKEND,
               port_sub: str = PORT_FRONTEND,
               port_sync: str = PORT_SYNC_HOST,
               port_killsig: str = PORT_KILL,
               **_):
    # TODO: extend the function argument footprint to user-specific function.
    """Constructor of the TemplatePipeline Node.

    Args:
        host_ip (str): IP address of the local master Broker.
        stream_out_spec (dict): Mapping of corresponding Stream object parameters to user-defined configuration values.
        stream_in_specs (list[dict]): List of mappings of user-configured incoming modalities.
        logging_spec (dict): Mapping of Storage object parameters to user-defined configuration values.
        port_pub (str, optional): Local port to publish to for local master Broker to relay. Defaults to PORT_BACKEND.
        port_sub (str, optional): Local port to subscribe to for incoming relayed data from the local master Broker. Defaults to PORT_FRONTEND.
        port_sync (str, optional): Local port to listen to for local master Broker's startup coordination. Defaults to PORT_SYNC_HOST.
        port_killsig (str, optional): Local port to listen to for local master Broker's termination signal. Defaults to PORT_KILL.
    """

    super().__init__(host_ip=host_ip,
                     stream_out_spec=stream_out_spec,
                     stream_in_specs=stream_in_specs,
                     logging_spec=logging_spec,
                     port_pub=port_pub,
                     port_sub=port_sub,
                     port_sync=port_sync,
                     port_killsig=port_killsig)


  @classmethod
  def create_stream(cls, stream_spec: dict) -> TemplateStream:
    return TemplateStream(**stream_spec)


  def _process_data(self, topic: str, msg: dict) -> None:
    if self._is_continue_produce:
      ###################################
      # TODO: processing results of data.
      ###################################
      process_time_s: float = get_time()
      ###################################
      ###################################

      tag: str = "%s.data" % self._log_source_tag()
      # TODO: match data keys to device and substream names of the Stream object.
      self._publish(tag, time_s=process_time_s, data=process_time_s)
    else:
      self._send_end_packet()


  def _stop_new_data(self):
    # TODO: trigger the sensor's backend to stop generating new data.
    pass
  

  def _cleanup(self) -> None:
    # TODO: perform component-specific clean-up.
    super()._cleanup()
