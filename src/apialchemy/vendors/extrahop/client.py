import json
import sys

from requests.sessions import Session
from requests import Request, codes

from .. import BaseClient


class Client(BaseClient):
    _session = None

    def __init__(self, **kwargs):
        super(Client, self).__init__(**kwargs)

        self.apikey = kwargs.get('apikey')

    @staticmethod
    def _get_full_path(path=None):
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

    def get_metrics(self, **params):
        url = self.base_url + self._get_full_path('/metrics')

        for k in list(params.keys()):
            if params[k] is None:
                del params[k]

        kwargs = {
            'method': 'POST',
            'url': url,
            'headers': {
                'Content-type': 'application/json',
                'Accept': 'text/plain',
                'Authorization': 'ExtraHop apikey=' + self.apikey
            },
            'data': json.dumps(params)
        }

        r = self._request(**kwargs)

        if r.status_code != codes.ok:
            print(url, file=sys.stderr)

            r.raise_for_status()

        return r.json()

    def get_metrics_by_xid(self, xid):
        url = self.base_url + self._get_full_path('/metrics/next/' + str(xid))

        kwargs = {
            'method': 'GET',
            'url': url,
            'headers': {
                'Content-type': 'application/json',
                'Accept': 'text/plain',
                'Authorization': 'ExtraHop apikey=' + self.apikey
            }
        }

        r = self._request(**kwargs)

        if r.status_code != codes.ok:
            print(url, file=sys.stderr)

            r.raise_for_status()

        return r.json()
