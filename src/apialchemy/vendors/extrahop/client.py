import json
import sys

from requests.sessions import Session
from requests import Request, codes

DEFAULT_HOST = 'localhost'
DEFAULT_SCHEME = 'https'


class ExtraHopClient:
    _session = None

    def __init__(self, **kwargs):
        self.base_url = self._get_base_url(kwargs.get('scheme', DEFAULT_SCHEME),
                                           kwargs.get('host', DEFAULT_HOST),
                                           kwargs.get('port'))
        self.apikey = kwargs.get('apikey')
        self.verify = kwargs.get('verify', True)

    def _get_base_url(self, scheme, host, port):
        if ':' in host:
            host = '[' + host + ']'

        base_url = scheme + '://' + host

        if port is not None:
            base_url += ':' + port

        return base_url

    def _get_full_path(self, path=None):
        path = '/api/v1' + (path or '')

        return path

    def _get_session(self):
        if not self._session:
            self._session = Session()
            self._session.verify = self.verify

        return self._session

    def _request(self, **request_args):
        s = self._get_session()

        req = Request(**request_args)

        prepped = s.prepare_request(req)

        # Merge environment settings into session
        settings = s.merge_environment_settings(prepped.url, {}, None, None, None)

        return s.send(prepped, **settings)

    def get_metrics(self, **kwargs):
        path = self._get_full_path('/metrics')

        return self.request(path, kwargs, method='POST', query=False)

    def request(self, path, params=None, method='GET', use_json=True, query=True, headers=None):
        if not path.startswith('/'):
            path = '/' + path

        url = self.base_url + path

        params = params or {}

        for k in list(params.keys()):
            if params[k] is None:
                del params[k]

        headers = headers or {}

        kwargs = {
            'method': method,
            'url': url,
            'headers': {
                'Authorization': 'ExtraHop apikey=' + self.apikey
            }
        }

        if method == 'GET' or query:
            kwargs['params'] = params
        else:
            kwargs['data'] = json.dumps(params)

            if not headers:
                headers = {
                    'Content-type': 'application/json',
                    'Accept': 'text/plain'
                }

        kwargs['headers'].update(headers)

        r = self._request(**kwargs)

        if r.status_code != codes.ok:
            print(url, file=sys.stderr)

            r.raise_for_status()

        return r.json() if use_json else r.text
