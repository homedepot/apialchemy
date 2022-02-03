from abc import ABCMeta, abstractmethod

DEFAULT_HOST = 'localhost'
DEFAULT_SCHEME = 'https'


class BaseClient:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, **kwargs):
        self.base_url = self._get_base_url(
            kwargs.get('scheme', DEFAULT_SCHEME),
            kwargs.get('host', DEFAULT_HOST),
            kwargs.get('port')
        )
        self.verify = kwargs.get('verify', True)

    @staticmethod
    def _get_base_url(scheme, host, port):
        if ':' in host:
            host = '[' + host + ']'

        base_url = scheme + '://' + host

        if port is not None:
            base_url += ':' + port

        return base_url


class BaseService:
    __metaclass__ = ABCMeta

    _conn_params = {}

    @abstractmethod
    def __init__(self, scheme, conn_str):
        self._scheme = scheme
        self._conn_str = conn_str
