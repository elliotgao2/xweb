import json

from xweb.descriptors import HeaderDict
from xweb.status_code import status_code


class Response:
    """
    I have no words to describe this class
    """

    def __init__(self):
        self.body = None
        self.headers = HeaderDict()
        self.status = 200

    def __repr__(self):
        return '<Response {}>'.format(self.status)

    @property
    def status_detail(self):
        return status_code.get(str(self.status))

    @property
    def status_result(self):
        return str(self.status) + ' ' + self.status_detail

    @property
    def headers_result(self):
        return [(key, val) for key, val in self.headers.items()]

    @property
    def body_result(self):
        if self.body is None:
            self.headers['Content-Length'] = 0
            return ''
        if isinstance(self.body, int):
            self.headers['Content-Type'] = 'text/html'
            return str(self.body)
        if isinstance(self.body, str):
            self.headers['Content-Type'] = 'text/html'
            return self.body
        if isinstance(self.body, dict):
            self.headers['Content-Type'] = 'text/json'
            return json.dumps(self.body)
        if isinstance(self.body, bytes):
            self.headers['Content-Type'] = 'application/octet-stream'
            return self.body
        return str(self.body)
