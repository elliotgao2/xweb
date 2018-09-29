import asyncio
import logging
from email.utils import formatdate
from functools import partial
from http import HTTPStatus

import httptools
from gunicorn.workers.base import Worker

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

except ImportError:
    pass

__version__ = '0.1.0'
__author__ = 'Jiuli Gao'
__all__ = ('Request', 'Response', 'App', 'XWebWorker', 'HTTPException', 'Context')

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

    def send(self, *args):
        # logger.debug(f'{self.req.ip} {self.req.url} {self.res.status} {self.res.msg}')
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
        self.ctx.req.url = url.decode()

    def on_header(self, name, value):
        self.ctx.req.headers[name.decode()] = value.decode()

    def on_body(self, body):
        self.ctx.req.raw = body

    def on_message_complete(self):
        task = self.loop.create_task(self.handler(self.ctx))
        task.add_done_callback(self.ctx.send)

    def data_received(self, data):
        self.parser.feed_data(data)

    def connection_lost(self, exc):
        self.transport.close()


class XWebWorker(Worker):

    def run(self):
        loop = asyncio.get_event_loop()
        for sock in self.sockets:
            protocol = partial(HTTPProtocol, loop=loop, handler=self.app.callable)
            server = loop.create_server(protocol, sock=sock)
            loop.create_task(server)
        loop.run_forever()


class App:
    def __init__(self):
        self.handlers = []
        self.debug = True

    def use(self, fn):
        self.handlers.append(fn)

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

    def listen(self, port=8000, host="127.0.0.1", debug=True):
        self.debug = debug
        logger.setLevel(self.debug)
        loop = asyncio.get_event_loop()
        protocol = partial(HTTPProtocol, loop=loop, handler=self)
        server = loop.create_server(protocol, host=host, port=port)
        loop.create_task(server)
        try:
            print(f'Serving at http://{host}:{port}/')
            loop.run_forever()
        except KeyboardInterrupt:
            print('\r', end='\r')
            print('Server stopped!')
        server.close()
        loop.close()
