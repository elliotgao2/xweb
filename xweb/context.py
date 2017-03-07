from xweb.request import Request
from xweb.response import Response


class Context:
    def __init__(self, environ):
        self.request = Request(environ)
        self.response = Response()
