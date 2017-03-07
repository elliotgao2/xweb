import functools
from functools import update_wrapper


class CachedProperty:
    def __init__(self, func):
        update_wrapper(self, func)
        self.func = func

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = instance.__dict__[self.func.__name__] = self.func(instance)
        return value


class DictProperty:
    def __init__(self, storage, read_only=False):
        self.storage = storage
        self.read_only = read_only

    def __call__(self, func):
        functools.update_wrapper(self, func, updated=[])
        self.func = func
        self.name = func.__name__
        return self

    def __get__(self, instance, owner):
        if instance is None:
            return self
        storage = getattr(instance, self.storage)

        if self.name not in storage:
            storage[self.name] = self.func(instance)

        return storage[self.name]

    def __set__(self, instance, value):
        if self.read_only:
            raise AttributeError("Read-Only property.")
        getattr(instance, self.storage)[self.name] = value

    def __delete__(self, instance):
        if self.read_only:
            raise AttributeError("Read-Only property.")
        del getattr(instance, self.storage)[self.name]


class HeaderDict(dict):
    def __getattr__(self, item):
        if not hasattr(self, item):
            return None
        else:
            return getattr(self, item)

    def __setattr__(self, key, value):
        setattr(key.title().replace('_', '-'), value)
