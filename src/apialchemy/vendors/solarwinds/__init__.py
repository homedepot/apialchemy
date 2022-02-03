import os
import re
import urllib3

from orionsdk import SwisClient

from urllib import parse

from .. import BaseService


class Service(BaseService):
    def __init__(self, scheme, conn_str):
        super(Service, self).__init__(scheme, conn_str)

        pattern = re.compile(
            r"""
                (?P<username>[^:/]*)
                :(?P<password>.*)
                @(?:
                    \[(?P<ipv6host>[^/]+)\] |
                    (?P<ipv4host>[^/:]+)
                )
            """,
            re.X
        )

        m = pattern.match(self._conn_str)

        if m is not None:
            components = m.groupdict()

            ipv4host = components.pop('ipv4host')
            ipv6host = components.pop('ipv6host')

            self._conn_params['hostname'] = ipv4host or ipv6host
            self._conn_params['username'] = parse.unquote(components['username'])
            self._conn_params['password'] = parse.unquote(components['password'])

    @property
    def client(self):
        verify = os.getenv('APIALCHEMY_SOLARWINDS_SSL_VERIFY', 'true').lower() == 'true'

        if not verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        return SwisClient(*self._conn_params.values(), verify=verify)
