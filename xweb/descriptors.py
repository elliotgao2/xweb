from functools import update_wrapper


class CachedProperty:
    """
    Cache properties
    """

    def __init__(self, func):
        update_wrapper(self, func)
        self.func = func

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = instance.__dict__[self.func.__name__] = self.func(instance)
        return value


class DictProperty:
    """
    Properties could be modified in a excepted way
    """

    def __init__(self, storage, read_only=False):
        self.storage = storage
        self.read_only = read_only

    def __call__(self, func):
        update_wrapper(self, func, updated=[])
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


class HeaderDict:
    """
    Avoid attribute error.
    Header's keys in good format.
    """

    def __init__(self):
        self.store = {}

    def __getattr__(self, item):
        return self.store.get(item, None)

    def __getitem__(self, item):
        return self.store.get(item, None)

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise ValueError('headers key must be string but get key:{}'.format(type(key)))
        self.store[key.title().replace('_', '-')] = str(value)

    def items(self):
        return self.store.items()
