import os
import re
import urllib3

from github import Github

from urllib import parse

from .. import BaseService


class Service(BaseService):
    def __init__(self, scheme, conn_str):
        super(Service, self).__init__(scheme, conn_str)

        pattern = re.compile(
            r"""
                (?P<login_or_token>.*)
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

            components['login_or_token'] = parse.unquote(components['login_or_token'])

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

            components['base_url'] += '/api/v3'

            self._conn_params = components

    @property
    def client(self):
        verify = os.getenv('APIALCHEMY_GITHUB_SSL_VERIFY', 'true').lower() == 'true'

        if not verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        return Github(verify=verify, **self._conn_params)

    @staticmethod
    def get_file_contents(client, org, repo, path, branch):
        repo = client.get_repo(org + '/' + repo)

        contents = repo.get_contents(path, ref=branch)

        return contents.decoded_content
