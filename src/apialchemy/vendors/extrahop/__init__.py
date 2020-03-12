import os
import re
import urllib3

from urllib import parse

from .. import BaseService

from .client import ExtraHopClient


class Service(BaseService):
    _conn_params = {}

    application = None

    def __init__(self, scheme, conn_str):
        super(Service, self).__init__(scheme, conn_str)

        pattern = re.compile(
            r"""
                (?P<apikey>[^:/]*)
                @(?:
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

            components['apikey'] = parse.unquote(components['apikey'])

            if self._scheme is not None:
                components['scheme'] = self._scheme

            ipv4host = components.pop('ipv4host')
            ipv6host = components.pop('ipv6host')

            components['host'] = ipv4host or ipv6host

            self._conn_params = components

    @property
    def client(self):
        verify = os.getenv('APIALCHEMY_EXTRAHOP_SSL_VERIFY', 'true').lower() == 'true'

        if not verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        return ExtraHopClient(**self._conn_params, verify=verify)
