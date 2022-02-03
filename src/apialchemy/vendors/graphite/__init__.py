import re

from urllib import parse

from .. import BaseService

from .client import Client


class Service(BaseService):
    def __init__(self, scheme, conn_str):
        super(Service, self).__init__(scheme, conn_str)

        pattern = re.compile(
            r"""
                (?:
                    \[(?P<ipv6host>[^/]+)\] |
                    (?P<ipv4host>[^/:]+)
                )
                (?::(?P<port>[\d]+))?
                (?:/(?P<prefix>.*))?
            """,
            re.X
        )

        m = pattern.match(self._conn_str)

        if m is not None:
            components = m.groupdict()

            ipv4host = components.pop('ipv4host')
            ipv6host = components.pop('ipv6host')

            components['host'] = ipv4host or ipv6host

            port = components.pop('port')

            if port is not None:
                components['port'] = int(port)

            prefix = components.pop('prefix')

            if prefix is not None:
                components['prefix'] = parse.unquote(prefix).strip('.')

            self._conn_params = components

    @property
    def client(self):
        return Client(**self._conn_params)
