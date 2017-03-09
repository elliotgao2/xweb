import threading
from functools import partial


class LocalStorage(dict):
    """
    Store all context into the same dict
    """
    thread_context_map = {}

    @classmethod
    def load_context(cls, name):
        return getattr(cls.thread_context_map[str(threading.current_thread().ident)], name)

    @classmethod
    def push(cls, identify, ctx):
        cls.thread_context_map[str(identify)] = ctx


class LocalProxy:
    """
    Inspired by flask
    """

    def __init__(self, fun):
        self.__dict__['fun'] = fun

    def __getattr__(self, item):
        if not hasattr(self.fun(), item):
            raise AttributeError
        return getattr(self.fun(), item)

    def __setattr__(self, key, value):
        if not hasattr(self.fun(), key):
            raise AttributeError
        setattr(self.fun(), key, value)


request = LocalProxy(partial(LocalStorage.load_context, 'request'))
response = LocalProxy(partial(LocalStorage.load_context, 'response'))
