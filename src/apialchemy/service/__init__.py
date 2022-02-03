import importlib
import re


def parse_uri(uri):
    pattern = re.compile(
        r'^(?P<vendor>\w+)(?:\+(?P<scheme>http|https|proxy))?://(?P<conn_str>.*)',
        re.X,
    )

    m = pattern.match(uri)

    if m is not None:
        components = m.groupdict()

        return ServiceConnection(components['vendor'], components['scheme'], components['conn_str'])

    return None


def create_service(uri):
    sc = parse_uri(uri)

    if sc is not None:
        return Service.create(sc)

    return None


class ServiceConnection:
    def __init__(self, vendor, scheme, conn_str):
        self.vendor = vendor
        self.scheme = scheme
        self.conn_str = conn_str


class Service:
    @staticmethod
    def create(sc):
        module = importlib.import_module('apialchemy.vendors.' + sc.vendor)

        return module.Service(sc.scheme, sc.conn_str)
