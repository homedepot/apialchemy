import base64

from prometheus_client import delete_from_gateway, push_to_gateway, pushadd_to_gateway

from urllib3 import PoolManager

from .. import BaseClient


class Client(BaseClient):
    def __init__(self, **kwargs):
        super(Client, self).__init__(**kwargs)

        self.username = kwargs.get('username')
        self.password = kwargs.get('password')

    def _pushgateway_handler(self, url, method, timeout, headers, data):
        username = self.username
        password = self.password
        verify = self.verify

        def handle():
            if username is not None and password is not None:
                auth_value = '{0}:{1}'.format(username, password).encode('utf-8')
                auth_token = base64.b64encode(auth_value)
                auth_header = b'Basic ' + auth_token
                headers.append(['Authorization', auth_header])

            cert_reqs = 'CERT_REQUIRED' if verify else 'CERT_NONE'

            http = PoolManager(cert_reqs=cert_reqs)

            resp = http.request(method, url, headers=dict(headers), body=data, timeout=timeout)

            if resp.status >= 400:
                raise IOError("error talking to pushgateway: {0} {1}".format(resp.status, resp.reason))

        return handle

    def delete(self, **kwargs):
        if 'handler' in kwargs.keys():
            handler = kwargs.pop('handler')
        else:
            handler = None

        if not callable(handler):
            handler = self._pushgateway_handler

        delete_from_gateway(self.base_url, handler=handler, **kwargs)

    def push(self, **kwargs):
        if 'handler' in kwargs.keys():
            handler = kwargs.pop('handler')
        else:
            handler = None

        if not callable(handler):
            handler = self._pushgateway_handler

        strict = kwargs.pop('strict') if 'strict' in kwargs.keys() else False

        if strict:
            pushadd_to_gateway(self.base_url, handler=handler, **kwargs)
        else:
            push_to_gateway(self.base_url, handler=handler, **kwargs)
