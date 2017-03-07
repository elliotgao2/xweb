import cgi
import os
from urllib.parse import parse_qsl

from xweb.descriptors import DictProperty


class HeaderDict(dict):
    def __getattr__(self, item):
        if not hasattr(self, item):
            return None
        else:
            return getattr(self, item)


class File:
    def __init__(self, file, name, filename):
        self.file = file
        self.name = name
        self.filename = filename

    def _copy_file(self, fp, chunk_size=2 ** 16):
        buf = self.file.read(chunk_size)
        while buf:
            fp.write(buf)
            buf = self.file.read(chunk_size)
        self.file.seek(self.file.tell())

    def save(self, destination, overwrite=False, chunk_size=2 ** 16):
        if isinstance(destination, str):
            if os.path.isdir(destination):
                destination = os.path.join(destination, self.filename)
            if not overwrite and os.path.exists(destination):
                raise IOError('File exists.')
            with open(destination, 'wb') as fp:
                self._copy_file(fp, chunk_size)
        else:
            self._copy_file(destination, chunk_size)


class Request:
    def __init__(self, environ):
        self.environ = environ
        self.storage = {}

    @DictProperty('storage', read_only=True)
    def path(self):
        return self.environ.get('PATH_INFO', '')

    @DictProperty('storage', read_only=True)
    def method(self):
        return self.environ.get('REQUEST_METHOD', 'GET').upper()

    @DictProperty('storage', read_only=True)
    def headers(self):
        result = HeaderDict()
        for key in self.environ:
            if key[:5] == 'HTTP_':
                result[key[:5].title().replace('_', '-')] = self.environ[key]
            elif key in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                result[key.title().replace('_', '-')] = self.environ[key]
        return result

    @DictProperty('storage', read_only=True)
    def ip(self):
        return self.environ.get('REMOTE_ADDR')

    @DictProperty('storage', read_only=True)
    def hostname(self):
        return self.environ.get('REMOTE_HOST')

    @DictProperty('storage', read_only=True)
    def query_string(self):
        return self.environ.get('QUERY_STRING')

    @DictProperty('storage', read_only=True)
    def query(self):
        query = {}
        for i in self.query_string.split('&'):
            key, value = i.split("=")
            query[key] = value
        return query

    @DictProperty('storage', read_only=True)
    def body(self):
        content_length = int(self.environ.get('CONTENT_LENGTH', 0))
        return self.environ['wsgi.input'].read(content_length).decode('utf-8')

    # @property
    # def headers(self):
    #     return self.headers.get('Content-Type', 'application/x-www-form-urlencoded')

    @DictProperty('storage', read_only=True)
    def data(self):
        pass

    @DictProperty('storage', read_only=True)
    def content_type(self):
        return self.environ.get('CONTENT_TYPE', '').lower()

    @DictProperty('storage', read_only=True)
    def content_length(self):
        return int(self.environ.get('CONTENT_LENGTH') or -1)

    @DictProperty('storage', read_only=True)
    def post(self):
        result = {}

        if not self.content_type.startswith('multipart/'):
            pairs = parse_qsl(self.body)
            for key, value in pairs:
                result[key] = value
            return result

        safe_env = {'QUERY_STRING': ''}  # Build a safe environment for cgi
        for key in ('REQUEST_METHOD', 'CONTENT_TYPE', 'CONTENT_LENGTH'):
            if key in self.environ:
                safe_env[key] = self.environ[key]

        data = cgi.FieldStorage(fp=self.body, environ=safe_env, keep_blank_values=True)

        data = data.list or []

        for item in data:
            if item.filename:
                result[item.name] = File(item.file,
                                         item.name,
                                         item.filename)
            else:
                result[item.name] = item.value

        return result

    @DictProperty('environ', read_only=True)
    def forms(self):
        forms = {}
        for name, item in self.post.items():
            if not isinstance(item, File):
                forms[name] = item
        return forms
