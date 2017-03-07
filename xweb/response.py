import json

from xweb.descriptors import HeaderDict


class Response:
    def __init__(self):
        self.body = None
        self.headers = HeaderDict()
        self.status = '200 OK'

    def __repr__(self):
        return '<Response {}>'.format(self.status)

    def get_status(self):
        return self.status

    def get_header(self):
        return [(key, val) for key, val in self.headers.items()]

    def get_body(self):
        if self.body is None:
            self.headers['Content-Length'] = '0'
            return ''
        if isinstance(self.body, str):
            self.headers['Content-Type'] = 'text/plain'
            return self.body
        if isinstance(self.body, dict):
            self.headers['Content-Type'] = 'text/json'
            return json.dumps(self.body)
        if isinstance(self.body, bytes):
            self.headers['Content-Type'] = 'application/octet-stream'
            return self.body
