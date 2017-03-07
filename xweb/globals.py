import threading
from functools import partial


class LocalStorage(dict):
    """"""
    thread_context_map = {}

    @classmethod
    def load_context(cls, name):
        return getattr(cls.thread_context_map[str(threading.current_thread().ident)], name)

    @classmethod
    def push(cls, identify, ctx):
        cls.thread_context_map[str(identify)] = ctx


class LocalProxy:
    def __init__(self, fun):
        self.fun = fun

    def __getattr__(self, item):
        if not hasattr(self.fun(), item):
            raise AttributeError
        return getattr(self.fun(), item)


request = LocalProxy(partial(LocalStorage.load_context, 'request'))
response = LocalProxy(partial(LocalStorage.load_context, 'response'))
