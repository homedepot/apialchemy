import base64
import ssl

from prometheus_client import delete_from_gateway, push_to_gateway, pushadd_to_gateway

from urllib.request import build_opener, Request, HTTPHandler, HTTPSHandler
from urllib.parse import urlparse

DEFAULT_HOST = 'localhost'
DEFAULT_SCHEME = 'https'


class PushgatewayClient:
    _session = None

    def __init__(self, **kwargs):
        self.base_url = self._get_base_url(kwargs.get('scheme', DEFAULT_SCHEME),
                                           kwargs.get('host', DEFAULT_HOST),
                                           kwargs.get('port'))
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.verify = kwargs.get('verify', True)

    def _get_base_url(self, scheme, host, port):
        if ':' in host:
            host = '[' + host + ']'

        base_url = scheme + '://' + host

        if port is not None:
            base_url += ':' + port

        return base_url

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

            url_components = urlparse(url)

            if not url_components.scheme or url_components.scheme != 'https':
                url_handler = HTTPHandler
            else:
                context = ssl.SSLContext()

                if verify:
                    context.verify_mode = ssl.CERT_REQUIRED
                else:
                    context.verify_mode = ssl.CERT_NONE

                url_handler = HTTPSHandler(context=context)

            request = Request(url, data=data)
            request.get_method = lambda: method

            for k, v in headers:
                request.add_header(k, v)

            resp = build_opener(url_handler).open(request, timeout=timeout)

            if resp.code >= 400:
                raise IOError("error talking to pushgateway: {0} {1}".format(
                    resp.code, resp.msg))

        return handle

    def delete(self, **kwargs):
        if 'handler' in kwargs:
            handler = kwargs.pop('handler')
        else:
            handler = None

        if not callable(handler):
            handler = self._pushgateway_handler

        delete_from_gateway(self.base_url, handler=handler, **kwargs)

    def push(self, **kwargs):
        if 'handler' in kwargs:
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
