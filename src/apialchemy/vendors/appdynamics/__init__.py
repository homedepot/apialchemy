import os
import re
import urllib3

from urllib import parse

from appd.request import AppDynamicsClient

from .. import BaseService


class Service(BaseService):
    application = None

    def __init__(self, scheme, conn_str):
        super(Service, self).__init__(scheme, conn_str)

        pattern = re.compile(
            r"""
                (?P<username>[^@:/]*)
                (?:@(?P<account>[^/:]+))?
                :(?P<password>.*)
                @(?:
                    \[(?P<ipv6host>[^/]+)\] |
                    (?P<ipv4host>[^/:]+)
                )
                (?::(?P<port>[\d]+))?
                (?:/(?P<application>.*))?
            """,
            re.X
        )

        m = pattern.match(self._conn_str)

        if m is not None:
            components = m.groupdict()

            components['username'] = parse.unquote(components['username'])

            account = components.pop('account')

            if account is not None:
                components['account'] = parse.unquote(account)

            components['password'] = parse.unquote(components['password'])

            ipv4host = components.pop('ipv4host')
            ipv6host = components.pop('ipv6host')

            host = ipv4host or ipv6host

            if self._scheme is not None:
                scheme = self._scheme
            else:
                scheme = 'https'

            components['base_url'] = scheme + '://' + host

            port = components.pop('port')

            if port is not None:
                components['base_url'] += ':' + port

            application = components.pop('application')

            if application is not None:
                self.application = parse.unquote(application)

            self._conn_params = components

    @property
    def client(self):
        verify = os.getenv('APIALCHEMY_APPD_SSL_VERIFY', 'true').lower() == 'true'

        if not verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        return AppDynamicsClient(verify=verify, **self._conn_params)

    @staticmethod
    def get_application_component_id(client, application_id, name):
        result = client.get_tiers(application_id)

        for t in result:
            if t.name == name:
                return t.id

        return None

    @staticmethod
    def get_application_id(client, name):
        for a in client.get_applications():
            if a.name == name:
                return a.id

        return None

    @staticmethod
    def get_business_transaction_id(client, application_id, name):
        result = client.get_bt_list(application_id)

        for bt in result:
            if bt.name == name:
                return bt.id

        return None
