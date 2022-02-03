import json

from wavefront_sdk.client_factory import WavefrontClientFactory
from wavefront_sdk.common import metric_to_line_data

from .. import BaseClient


class Client(BaseClient):
    def __del__(self):
        self._sender.close()

    def __init__(self, **kwargs):
        self._prefix = kwargs.get('prefix')

        client_factory = WavefrontClientFactory()

        client_factory.clients = []

        client_factory.add_client(url=self._get_base_url(
            kwargs.get('scheme'),
            kwargs.get('host'),
            kwargs.get('port')
        ))

        self._sender = client_factory.get_client()

    def send(self, source, metrics):
        metric_data = []

        for metric_name, info in metrics.items():
            for json_tag_data, (metric, timestamp) in info.items():
                metric_data.append(metric_to_line_data(
                    name=('%s.%s' % (self._prefix, metric_name) if self._prefix is not None else metric_name).strip('.'),
                    value=metric,
                    timestamp=timestamp,
                    source='',
                    tags=json.loads(json_tag_data),
                    default_source=source
                ))

        self._sender.send_metric_now(metric_data)
