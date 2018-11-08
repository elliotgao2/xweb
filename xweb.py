import asyncio
import multiprocessing
import os
import socket
import ujson as json
from email.utils import formatdate
from functools import partial
from http import HTTPStatus

import httptools
from jsonschema import Draft4Validator, ErrorTree

__version__ = '3.0.1'


class HTTPException(Exception):
    def __init__(self, status, msg=None, properties=None):
        self.properties = properties
        self.msg = msg
        self.status = status


class Request:
    def __init__(self):
        self.headers = {}
        self.method = "HEAD"
        self.url = "/"
        self.raw = None
        self.ip = None

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)


class Response:
    def __init__(self):
        self.body = ""
        self.status = 200
        self.msg = ""
        self.headers = {
            'Date': formatdate(timeval=None, localtime=False, usegmt=True),
            'Content-Type': 'text/plain'
        }

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __bytes__(self):
        http_status = HTTPStatus(self.status)
        http_status_bytes = f"HTTP/1.1 {http_status.value} {http_status.phrase}".encode()
        http_body_bytes = self.body.encode()
        self.headers['Content-Length'] = len(http_body_bytes)
        http_header_bytes = "\r\n".join([f'{k}: {v}' for k, v in self.headers.items()]).encode()
        return http_status_bytes + b'\r\n' + http_header_bytes + b'\r\n\r\n' + http_body_bytes


class Context:
    def __init__(self):
        self.req = Request()
        self.resp = Response()
        self.write = None

    def send(self, _):
        self.write(bytes(self.resp))

    def check(self, value, status=400, msg='', properties=""):
        if not value:
            self.abort(status=status, msg=msg, properties=properties)

    def abort(self, status, msg="", properties=""):
        raise HTTPException(status=status, msg=msg, properties=properties)

    def __getattr__(self, item):
        return getattr(self.req, item)

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    @property
    def headers(self):
        return self.resp.headers

    @property
    def json(self):
        return json.loads(self.body)

    @property
    def body(self):
        return self.resp.body

    @body.setter
    def body(self, value):
        self.resp.body = value

    @property
    def status(self):
        return self.resp.status

    @status.setter
    def status(self, value):
        self.resp.status = value

    @property
    def msg(self):
        return self.resp.msg

    @msg.setter
    def msg(self, value):
        self.resp.msg = value


class HTTPProtocol(asyncio.Protocol):

    def __init__(self, handler, loop):
        self.parser = None
        self.transport = None
        self.handler = handler
        self.loop = loop
        self.ctx = None

    def connection_made(self, transport):
        self.parser = httptools.HttpRequestParser(self)
        self.transport = transport

    def on_url(self, url):
        self.ctx = Context()
        self.ctx.write = self.transport.write
        url = httptools.parse_url(url)
        self.ctx.req.path = url.path.decode()
        self.ctx.req.method = self.parser.get_method().decode()

    def on_header(self, name, value):
        self.ctx.req.headers[name.decode()] = value.decode()

    def on_body(self, body):
        self.ctx.req.raw += body

    def on_message_complete(self):
        task = self.loop.create_task(self.handler(self.ctx))
        task.add_done_callback(self.ctx.send)

    def data_received(self, data):
        self.parser.feed_data(data)

    def connection_lost(self, exc):
        self.transport.close()


class App:
    def __init__(self):
        self.workers = set()
        self.routes = {}

    def serve(self, sock):
        loop = asyncio.new_event_loop()
        server = loop.create_server(partial(HTTPProtocol, loop=loop, handler=self), sock=sock)
        loop.create_task(server)
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            server.close()
            loop.close()

    def listen(self, port=8000, host="127.0.0.1", workers=multiprocessing.cpu_count()):
        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

        pid = os.getpid()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(False)
        sock.bind((host, port))
        os.set_inheritable(sock.fileno(), True)

        try:
            print(f'[{pid}] Listening at: http://{host}:{port}')
            print(f'[{pid}] Workers: {workers}')
            for _ in range(workers):
                worker = multiprocessing.Process(target=self.serve, kwargs=dict(sock=sock))
                worker.daemon = True
                worker.start()
                print(f'[{pid}] Starting worker with pid: {worker.pid}')
                self.workers.add(worker)
            for worker in self.workers:
                worker.join()
        except KeyboardInterrupt:
            print('\r', end='\r')
            print(f'[{pid}] Server soft stopping')
            for worker in self.workers:
                worker.terminate()
                worker.join()
            print(f'[{pid}] Server stopped successfully!')
        sock.close()

    async def __call__(self, ctx):
        try:
            handler = self.routes.get(ctx.req.path)
            if not handler:
                raise HTTPException(404)
            await handler(ctx).request()
        except HTTPException as e:
            ctx.status = e.status
            ctx.body = e.msg or HTTPStatus(e.status).phrase
            ctx.msg = e.properties


class Controller:
    def __init__(self, ctx):
        self.ctx = ctx

    async def request(self):
        handler = getattr(self, self.ctx.req.method.lower(), None)
        if not handler:
            raise HTTPException(405)
        await handler()


class RESTController(Controller):

    async def request(self):
        self.ctx.headers['Content-Type'] = 'application/json'
        await super().request()
        self.ctx.body = json.dumps(self.ctx.body)


class Model:
    schema = {}

    @classmethod
    def validate(cls, data):
        errors = ErrorTree(Draft4Validator(cls.schema).iter_errors(data)).errors
        if errors:
            raise HTTPException(400, msg=str(errors))
        return data
