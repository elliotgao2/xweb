import asyncio
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

__all__ = ('Request', 'Response', 'App', 'XWebWorker', 'HTTPException')


class HTTPException(Exception):
    """HTTPException"""

    def __init__(self, status, msg, properties):
        self.properties = properties
        self.msg = msg
        self.status = status


class Request:
    def __init__(self,
                 method="",
                 url="",
                 href="",
                 path="",
                 querystring="",
                 host="",
                 raw="",
                 ip="",
                 ):
        self.headers = {}
        self.method = method
        self.url = url
        self.href = href
        self.path = path
        self.querystring = querystring
        self.host = host
        self.raw = raw
        self.ip = ip

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)


class Response:
    def __init__(self,
                 body="",
                 status=200,
                 message="",
                 header_sent="",
                 ):
        self.body = body
        self.status = status
        self.message = message
        self.header_sent = header_sent

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __bytes__(self):
        http_status = HTTPStatus(self.status)
        length = len(self.body)
        return f"HTTP/1.1 {http_status.value} {http_status.phrase}\r\nContent-Type: text/plain\r\nContent-Length: {length}\r\n\r\n{self.body}".encode()


class Context:
    def __init__(self):
        self.req = Request()
        self.res = Response()

    def __getattr__(self, name):
        return getattr(self.req, name)

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def check(self, value, status=500, msg='', properties=None):
        if not value:
            self.abort(status=status, msg=msg, properties=properties)

    def abort(self, status, msg, properties):
        raise HTTPException(status=status, msg=msg, properties=properties)


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

    def on_url(self, url):
        self.ctx.req.method = self.parser.get_method()
        parsed_url = httptools.parse_url(url)
        self.ctx.req.url = url
        self.ctx.req.host = parsed_url.host
        self.ctx.req.path = parsed_url.path
        self.ctx.req.port = parsed_url.port
        self.ctx.req.querystring = parsed_url.query

    def on_header(self, name, value):
        self.ctx.req.headers[name] = value

    def on_body(self, body):
        self.ctx.req.raw = body

    def on_message_complete(self):
        task = self.loop.create_task(self.handler(self.ctx))
        task.add_done_callback(self.done_callback)

    def done_callback(self, future):
        self.transport.write(bytes(self.ctx.res))

    def data_received(self, data):
        self.parser.feed_data(data)

    def eof_received(self):
        self.transport.close()

    def connection_lost(self, exc):
        self.transport.close()


class XWebWorker(Worker):

    def run(self):
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        loop = asyncio.get_event_loop()
        for sock in self.sockets:
            protocol = partial(HTTPProtocol, loop=loop, handler=self.app.callable)
            server = loop.create_server(protocol, sock=sock)
            loop.create_task(server)
        loop.run_forever()


class App:
    def __init__(self):
        self.handlers = []

    def use(self, fn):
        self.handlers.append(fn)

    async def __call__(self, ctx):
        next_fn = None
        for handler in self.handlers[::-1]:
            if next_fn is not None:
                next_fn = partial(handler, ctx=ctx, fn=next_fn)
            else:
                next_fn = partial(handler, ctx=ctx)
        try:
            await next_fn()
        except HTTPException as e:
            ctx.res.body = e.msg
            ctx.res.status = e.status

    def listen(self, port=8000, host="127.0.0.1"):
        loop = asyncio.get_event_loop()
        protocol = partial(HTTPProtocol, loop=loop, handler=self)
        server = loop.create_server(protocol, host=host, port=port)
        loop.create_task(server)
        try:
            print(f'Listen http://{host}:{port}')
            loop.run_forever()
        except KeyboardInterrupt:
            print('\r', end='\r')
            print('Stopped')
        server.close()
        loop.close()
