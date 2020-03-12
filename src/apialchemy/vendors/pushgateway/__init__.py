import os
import re
import urllib3

from urllib import parse

from .. import BaseService

from .client import PushgatewayClient


class Service(BaseService):
    _conn_params = {}

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

            if components['username'] is not None and components['password'] is not None:
                components['username'] = parse.unquote(components['username'])
                components['password'] = parse.unquote(components['password'])

            if self._scheme is not None:
                components['scheme'] = self._scheme

            ipv4host = components.pop('ipv4host')
            ipv6host = components.pop('ipv6host')

            components['host'] = ipv4host or ipv6host

            self._conn_params = components

    @property
    def client(self):
        verify = os.getenv('APIALCHEMY_PUSHGATEWAY_SSL_VERIFY', 'true').lower() == 'true'

        if not verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        return PushgatewayClient(**self._conn_params, verify=verify)
