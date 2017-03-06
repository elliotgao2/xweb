import json
from cgi import parse_header
from functools import partial



class Request:
    def __init__(self, environ):
        self.environ = environ

    @property
    def path(self):
        return self.environ.get('PATH_INFO')

    @property
    def method(self):
        return self.environ.get('REQUEST_METHOD')

    @property
    def ip(self):
        return self.environ.get('REMOTE_ADDR')

    @property
    def host(self):
        return self.environ.get('REMOTE_HOST')

    @property
    def query_string(self):
        return self.environ.get('QUERY_STRING')

    @property
    def query(self):
        query = {}
        for i in self.query_string.split('&'):
            key, value = i.split("=")
            query[key] = value
        return query

    @property
    def body(self):
        content_length = int(self.environ.get('CONTENT_LENGTH', 0))
        return self.environ['wsgi.input'].read(content_length).decode('utf-8')

    @property
    def content_type(self):
        return self.environ.get('CONTENT_TYPE', 'application/x-www-form-urlencoded')

    # @property
    # def headers(self):
    #     return self.headers.get('Content-Type', 'application/x-www-form-urlencoded')

    @property
    def data(self):
        content_type, parameters = parse_header(self.content_type)
        if content_type == 'application/x-www-form-urlencoded':
            data = {}
            for i in self.body.split('&'):
                key, value = i.split("=")
                data[key] = value
            return data
        # elif content_type == 'multipart/form-data':
        #     # TODO I need a better form-data parser
        #     parameters['boundary'] = parameters['boundary'].encode('utf-8')
        #     return parse_multipart(self.environ['wsgi.input'], parameters)
        elif content_type == 'application/json':
            return json.loads(self.body)
        elif content_type == 'text/plain':
            return self.body
        else:
            return self.body


