import base64
import os
import re
import urllib3

from urllib import parse

from prometheus_api_client import PrometheusConnect, Metric, MetricsList

from .. import BaseService


class Service(BaseService):
    def __init__(self, scheme, conn_str):
        super(Service, self).__init__(scheme, conn_str)

        pattern = re.compile(
            r"""
                (?:
                    (?P<username>[^:/]*)
                    :(?P<password>.*)@
                )?
                (?:
                    \[(?P<ipv6host>[^/]+)\] |
                    (?P<ipv4host>[^/:]+)
                )
                (?::(?P<port>[\d]+))?
            """,
            re.X
        )

        m = pattern.match(self._conn_str)

        if m is not None:
            components = m.groupdict()

            username = components.pop('username')
            password = components.pop('password')

            if username is not None and password is not None:
                encoding = os.getenv('APIALCHEMY_PROMETHEUS_AUTH_ENCODING', 'utf-8')

                auth_str = '%s:%s' % (parse.unquote(username), parse.unquote(password))
                auth_bytes = auth_str.encode(encoding)
                base64_bytes = base64.b64encode(auth_bytes)

                components['headers'] = {
                    'Authorization': base64_bytes.decode(encoding)
                }

            ipv4host = components.pop('ipv4host')
            ipv6host = components.pop('ipv6host')

            host = ipv4host or ipv6host

            if self._scheme is not None:
                scheme = self._scheme
            else:
                scheme = 'http'

            components['url'] = scheme + '://' + host

            port = components.pop('port')

            if port is not None:
                components['url'] += ':' + port

            self._conn_params = components

    @property
    def client(self):
        verify = os.getenv('APIALCHEMY_PROMETHEUS_SSL_VERIFY', 'true').lower() == 'true'

        if not verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        return PrometheusConnect(disable_ssl=not verify, **self._conn_params)

    @staticmethod
    def get_metric_obj(metric_data):
        return Metric(metric_data)

    @staticmethod
    def get_metric_obj_list(metric_data):
        return MetricsList(metric_data)
