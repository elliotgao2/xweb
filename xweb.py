import asyncio
import logging
import multiprocessing
import os
import socket
from email.utils import formatdate
from functools import partial
from http import HTTPStatus

import httptools

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

except ImportError:
    pass

__version__ = '0.1.1'
__author__ = 'Jiuli Gao'
__all__ = ('Request', 'Response', 'App', 'HTTPException', 'Context')

FORMAT = '[%(asctime)-15s] %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('xweb')
logger.setLevel(logging.DEBUG)


class HTTPException(Exception):
    def __init__(self, status, msg, properties):
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
        self.body = "Hello Xweb!"
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
        http_status_raw = f"HTTP/1.1 {http_status.value} {http_status.phrase}\r\n".encode()
        http_body_raw = self.body.encode()
        self.headers['Content-Length'] = len(http_body_raw)
        http_header_raw = "".join([f'{k}: {v}\r\n' for k, v in self.headers.items()]).encode() + b'\r\n'
        return http_status_raw + http_header_raw + http_body_raw


class Context:
    def __init__(self):
        self.req = Request()
        self.res = Response()
        self.write = None

    def send(self, _):
        self.write(bytes(self.res))

    def check(self, value, status=400, msg='', properties=""):
        if not value:
            self.abort(status=status, msg=msg, properties=properties)

    def abort(self, status, msg="", properties=""):
        raise HTTPException(status=status, msg=msg, properties=properties)

    def __getattr__(self, name):
        return getattr(self.req, name)

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)


class HTTPProtocol(asyncio.Protocol):

    def __init__(self, handler, loop):
        self.parser = None
        self.transport = None
        self.handler = handler
        self.loop = loop
        self.ctx = Context()

    def connection_made(self, transport):
        self.parser = httptools.HttpRequestParser(self)
        self.transport = transport
        client = transport.get_extra_info('peername')
        self.ctx.req.ip = client[0]
        self.ctx.write = self.transport.write

    def on_url(self, url):
        self.ctx.req.url = url

    def on_header(self, name, value):
        self.ctx.req.headers[name] = value

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
        self.handlers = []
        self.workers = set()

    def use(self, fn):
        self.handlers.append(fn)

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
        pid = os.getpid()
        print(f'[{pid}] Starting xweb {__version__}')
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
        if not self.handlers:
            return
        next_fn = None
        for handler in self.handlers[::-1]:
            if next_fn is not None:
                next_fn = partial(handler, ctx=ctx, fn=next_fn)
            else:
                next_fn = partial(handler, ctx=ctx)
        try:
            await next_fn()
        except HTTPException as e:
            ctx.res.status = e.status
            ctx.res.body = e.msg or HTTPStatus(e.status).phrase
            ctx.res.msg = e.properties
