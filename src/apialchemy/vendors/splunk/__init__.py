import os
import re
import urllib3

from time import sleep

from urllib import parse

from splunklib.client import connect
from splunklib import results

from .. import BaseService


class Service(BaseService):
    application = None

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
                (?::(?P<port>[\d]+))?
                (?:/(?P<application>.*))?
            """,
            re.X
        )

        m = pattern.match(self._conn_str)

        if m is not None:
            components = m.groupdict()

            components['username'] = parse.unquote(components['username'])
            components['password'] = parse.unquote(components['password'])

            if self._scheme is not None:
                components['scheme'] = self._scheme

            ipv4host = components.pop('ipv4host')
            ipv6host = components.pop('ipv6host')

            components['host'] = ipv4host or ipv6host

            port = components.pop('port')

            if port is not None:
                components['port'] = port

            application = components.pop('application')

            if application is not None:
                self.application = parse.unquote(application)

            self._conn_params = components

    @property
    def client(self):
        verify = os.getenv('APIALCHEMY_SPLUNK_SSL_VERIFY', 'true').lower() == 'true'

        if not verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        return connect(verify=verify, **self._conn_params)

    @staticmethod
    def search(client, query, **kwargs):
        if 'exec_mode' not in kwargs.keys():
            kwargs['exec_mode'] = 'blocking'

        job = client.search(query, **kwargs)

        if kwargs['exec_mode'] == 'normal':
            while True:
                while not job.is_ready():
                    pass

                if job['isDone'] == '1':
                    break

                sleep(2)

        result_count = int(job['resultCount'])
        offset = 0
        count = int(client.confs['limits']['restapi']['maxresultrows'])

        reader = []

        while offset < result_count:
            kwargs_paginate = {
                'count': count,
                'offset': offset
            }

            reader += results.ResultsReader(job.results(**kwargs_paginate))

            offset += count

        job.cancel()

        return reader
