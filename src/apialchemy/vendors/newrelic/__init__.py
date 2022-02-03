import os
import re
import urllib3

from urllib import parse

from .. import BaseService

from .client import Client


class Service(BaseService):
    account_id = None

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
                (?:/(?P<accountid>\d*))?
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

            account_id = components.pop('accountid')

            if account_id is not None:
                self.account_id = int(account_id)

            self._conn_params = components

    @property
    def client(self):
        verify = os.getenv('APIALCHEMY_NEWRELIC_SSL_VERIFY', 'true').lower() == 'true'

        if not verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        return Client(verify=verify, **self._conn_params)
