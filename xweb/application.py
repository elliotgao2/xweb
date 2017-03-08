import re
import threading

from xweb.context import Context
from xweb.descriptors import CachedProperty
from xweb.exception import HTTPError, RouteError
from xweb.globals import LocalStorage


class XWeb:
    def __init__(self):
        self.request_middlewares = []
        self.route_processors = []
        self.response_middlewares = []
        self.identify = str(threading.current_thread().ident)

    def __call__(self, environ, start_response):

        ctx = Context(environ)
        LocalStorage.push(self.identify, ctx)
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
                            raise HTTPError(405)

                            # if not matched:
                            #     raise HTTPError(404)

        except HTTPError as e:
            # ctx.response.body = e.args.get(1, None)
            ctx.response.status = e.args[0]
        finally:
            status = ctx.response.get_status()
            body = ctx.response.get_body()
            header = ctx.response.get_header()

            start_response(status, header)
            return [body.encode('utf-8')]

    @CachedProperty
    def processors(self):
        processors = []
        processors.extend(self.request_middlewares)
        processors.extend(self.route_processors)
        processors.extend(self.response_middlewares)
        return processors

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
                raise RouteError('Route {} repeat defining'.format(path))
            self.route_processors.append((pattern, methods, fn))

        return decorator

    def listen(self, port):
        """
        this server is just for developing. do not using this in production

        :param port: port
        :return:
        """
        from wsgiref.simple_server import make_server
        server = make_server('127.0.0.1', port, self)
        print('serve on 127.0.0.1:{port}'.format(port=port))
        server.serve_forever()
