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

    def query(self, query_str):
        url = self.base_url + '/graphql'

        params = {
            'query': query_str
        }

        kwargs = {
            'method': 'POST',
            'url': url,
            'headers': {
                'Content-type': 'application/json',
                'API-Key': self.apikey
            },
            'data': json.dumps(params)
        }

        r = self._request(**kwargs)

        if r.status_code != codes.ok:
            print(url, file=sys.stderr)

            r.raise_for_status()

        return r.json()
