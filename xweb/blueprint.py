import re

from xweb.exception import RouteError


class Blueprint:
    """Blueprint has the same function of the blueprint in flask
    """

    def __init__(self, prefix=''):
        self.prefix = prefix
        self.route_processors = []

    def route(self, path, methods=None):
        if methods is None:
            methods = ['GET']

        def decorator(fn):
            pattern = re.compile(
                re.sub(r':(?P<params>[a-z_]+)',
                       lambda m: '(?P<{}>[a-z0-9-]+)'.format(m.group('params')),
                       self.prefix + path).rstrip('/') + '/$')
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
