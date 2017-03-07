import re
import threading
from functools import partial, update_wrapper
from pprint import pprint

from xweb.context import Context
from xweb.exception import HTTPError, RouteError

thread_context_map = {}


class CachedProperty:
    def __init__(self, func):
        update_wrapper(self, func)
        self.func = func

    def __get__(self, instance, owner):
        if instance is None: return self
        value = instance.__dict__[self.func.__name__] = self.func(instance)
        return value


def load_context(name):
    return getattr(thread_context_map[str(threading.current_thread().ident)], name)


class Local:
    def __init__(self, fun):
        self.fun = fun

    def __getattr__(self, item):
        return getattr(self.fun(), item)


request = Local(partial(load_context, 'request'))
response = Local(partial(load_context, 'response'))


class XWeb:
    def __init__(self):
        self.request_middlewares = []
        self.route_processors = []
        self.response_middlewares = []

    def __call__(self, environ, start_response):
        identify = str(threading.current_thread().ident)
        ctx = Context(environ)
        thread_context_map[identify] = ctx
        matched = False

        try:
            for pattern, methods, fn in self.processors:

                if pattern is None:
                    fn()
                else:
                    match = pattern.match(ctx.request.path)
                    if match:
                        matched = True

                        if ctx.request.method in methods:
                            ctx.response.body = fn(**match.groupdict())
                        else:
                            HTTPError(415)

            if not matched:
                raise HTTPError(404)

        except HTTPError as e:
            ctx.response.body = '404 Not Found'
            ctx.response.status = '404 Not Found'
        finally:
            headers = [(key, val) for key, val in ctx.response.headers.items()]
            start_response(ctx.response.status, headers)
            return [str(ctx.response.body).encode('utf-8')]

    @CachedProperty
    def processors(self):
        self.request_middlewares.extend(self.route_processors)
        self.request_middlewares.extend(self.response_middlewares)
        return self.request_middlewares

    def middleware(self, middleware_type):
        def decorator(fn):
            if middleware_type == 'response':
                self.response_middlewares.extend([(None, None, fn)])
            else:
                self.request_middlewares.extend([(None, None, fn)])

        return decorator

    def route(self, path, methods=None):
        if methods is None:
            methods = ['GET']

        def decorator(fn):
            pattern = re.compile(
                re.sub(r':(?P<params>[a-z_]+)',
                       lambda m: '(?P<{}>[a-z0-9-]+)'.format(m.group('params')),
                       path) + '$')
            if pattern in map(lambda i: i[0], self.route_processors):
                raise RouteError('Routes repeat defining {}'.format(path))
            self.route_processors.append((pattern, methods, fn))

        return decorator

    def listen(self, port):
        from wsgiref.simple_server import make_server
        server = make_server('0.0.0.0', port, self)
        print('serve on 0.0.0.0:{port}'.format(port=port))
        server.serve_forever()
