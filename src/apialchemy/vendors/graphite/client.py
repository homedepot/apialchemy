from prometheus_client.bridge.graphite import GraphiteBridge


class Client:
    def __init__(self, host, port=2003, prefix=None):
        self._prefix = prefix

        self._gb = GraphiteBridge((host, port), tags=True)

    def push(self, **kwargs):
        if 'registry' in kwargs.keys():
            self._gb._registry = kwargs.pop('registry')

        if 'prefix' not in kwargs.keys() and self._prefix is not None:
            kwargs['prefix'] = self._prefix

        self._gb.push(**kwargs)

    def start(self, **kwargs):
        if 'registry' in kwargs.keys():
            self._gb._registry = kwargs.pop('registry')

        if 'prefix' not in kwargs.keys() and self._prefix is not None:
            kwargs['prefix'] = '%s.' % self._prefix

        self._gb.start(**kwargs)
