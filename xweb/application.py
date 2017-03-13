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
        self.exception_handlers = {}
        self.identify = str(threading.current_thread().ident)

    def __call__(self, environ, start_response):

        ctx = Context(environ)
        LocalStorage.push(self.identify, ctx)
        matched = False
        override = False
        try:
            for pattern, methods, fn in self.processors:

                if pattern is None:
                    result = fn()
                    if result is not None:
                        ctx.response.body = result
                        override = True
                        break
                else:
                    match = pattern.match(ctx.request.path)
                    if match:
                        matched = True
                        if ctx.request.method not in methods:
                            raise HTTPError(405)
                        else:
                            ctx.response.body = fn(**match.groupdict())

            if not matched and not override:
                raise HTTPError(404)

        except HTTPError as e:
            ctx.response.status = e.args[0]
            ctx.response.body = ctx.response.status_detail

            status_code = str(ctx.response.status)
            if status_code in self.exception_handlers:
                self.exception_handlers[str(status_code)]()
        finally:
            status = ctx.response.status_result
            body = ctx.response.body_result
            header = ctx.response.headers_result
            start_response(status, header)
            return [body.encode('utf-8')]

    def exception(self, status_code):
        def decorator(fn):
            self.exception_handlers[str(status_code)] = fn

        return decorator

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
                       path).rstrip('/') + '/$')
            if pattern in map(lambda i: i[0], self.route_processors):
                raise RouteError('Route {} repeat defining'.format(path))
            self.route_processors.append((pattern, methods, fn))

        return decorator

    def get(self, path):
        return self.route(path, methods=['GET'])

    def post(self, path):
        return self.route(path, methods=['POST'])

    def put(self, path):
        return self.route(path, methods=['PUT'])

    def patch(self, path):
        return self.route(path, methods=['PATCH'])

    def delete(self, path):
        return self.route(path, methods=['DELETE'])

    def option(self, path):
        return self.route(path, methods=['OPTION'])

    def head(self, path):
        return self.route(path, methods=['HEAD'])

    # def run(self, port):
    #
    #     project_dir = os.getcwd()
    #     start_time = max(os.stat(root).st_ctime for root, _, _ in os.walk(project_dir))
    #     last_time = start_time
    #
    #     while True:
    #         time.sleep(0.5)
    #         try:
    #             if last_time != start_time:
    #                 start_time = last_time
    #                 print(self.request_middlewares)
    #             else:
    #                 last_time = max(os.stat(root).st_ctime for root, _, _ in os.walk(project_dir))
    #         except KeyboardInterrupt:
    #             sys.exit(0)

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
