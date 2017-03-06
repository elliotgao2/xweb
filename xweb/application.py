import re
import threading
from functools import partial

from xweb.context import Context
from xweb.exception import HTTPError, RouteError

thread_context_map = {}


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
        self.processors = []

    def __call__(self, environ, start_response):
        identify = str(threading.current_thread().ident)
        ctx = Context(environ)
        thread_context_map[identify] = ctx

        for pattern, methods, fn in self.processors:
            try:
                if pattern is not None:
                    match = pattern.match(ctx.request.path)
                    if match:
                        if ctx.request.method in methods:
                            ctx.response.body = fn(**match.groupdict())
                            break
                        else:
                            HTTPError(415)
                else:
                    fn(ctx)
                raise HTTPError(404)
            except HTTPError as e:
                print(e.args[0])
                ctx.response.body = '404 Not Found'
                ctx.response.status = '404 Not Found'
            finally:
                headers = [(key, val) for key, val in ctx.response.headers.items()]
                start_response(ctx.response.status, headers)
                return [str(ctx.response.body).encode('utf-8')]

    def plugin(self, fn):
        self.processors.append((None, None, fn))

    def route(self, path, methods=None):
        if methods is None:
            methods = ['GET']

        def decorator(fn):
            pattern = re.compile(
                re.sub(r':(?P<params>[a-z_]+)',
                       lambda m: '(?P<{}>[a-z0-9-]+)'.format(m.group('params')),
                       path) + '$')
            if pattern in map(lambda i: i[0], self.processors):
                raise RouteError('Repeat defining routes {}'.format(path))
            self.processors.append((pattern, methods, fn))

        return decorator

    def listen(self, port):
        from wsgiref.simple_server import make_server
        server = make_server('0.0.0.0', port, self)
        print('serve on 0.0.0.0:{port}'.format(port=port))
        server.serve_forever()
