from abc import ABCMeta, abstractmethod


class BaseService:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, scheme, conn_str):
        self._scheme = scheme
        self._conn_str = conn_str
