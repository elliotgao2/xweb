import asyncio
import signal
from functools import partial

import httptools
import uvloop
from gunicorn.workers.base import Worker

__version__ = '0.1.0'
__author__ = 'Jiuli Gao'

__all__ = ('Request', 'Response', 'App', 'XWebWorker')


class Request:
    def __init__(self,
                 header="",
                 headers="",
                 method="",
                 url="",
                 original_url="",
                 origin="",
                 href="",
                 path="",
                 query="",
                 querystring="",
                 host="",
                 hostname="",
                 fresh="",
                 stale="",
                 socket="",
                 protocol="",
                 secure="",
                 ip="",
                 ips="",
                 ):
        self.header = header
        self.headers = headers
        self.method = method
        self.url = url
        self.original_url = original_url
        self.origin = origin
        self.href = href
        self.path = path
        self.query = query
        self.querystring = querystring
        self.host = host
        self.hostname = hostname
        self.fresh = fresh
        self.stale = stale
        self.socket = socket
        self.protocol = protocol
        self.secure = secure
        self.ip = ip
        self.ips = ips

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)


class Response:
    def __init__(self,
                 body="",
                 status="",
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


class Context:
    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)


class HttpProtocol(asyncio.Protocol):

    def __init__(self, handler, loop):
        self.parser = None
        self.transport = None
        self.handler = handler
        self.loop = loop
        self.headers = {}
        self.ctx = Context()

    def connection_made(self, transport):
        self.parser = httptools.HttpRequestParser(self)
        self.transport = transport

    def on_url(self, url):
        httptools.parse_url(url)

    def on_header(self, name, value):
        self.headers[name.decode()] = value.decode()

    def on_body(self, body):
        self.ctx.body = body

    def on_message_complete(self):
        task = self.loop.create_task(self.handler(self.ctx))
        task.add_done_callback(self.done_callback)

    def done_callback(self, future):
        body = self.ctx.body
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(body)}\r\n\r\n{body}".encode()
        self.transport.write(response)

    def data_received(self, data):
        self.parser.feed_data(data)

    def eof_received(self):
        self.transport.close()

    def connection_lost(self, exc):
        self.transport.close()


class XWebWorker(Worker):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self):
        loop = asyncio.get_event_loop()
        [loop.create_task(loop.create_server(partial(HttpProtocol, loop=loop, handler=self.app.callable), sock=sock))
         for sock in self.sockets]
        loop.run_forever()

    def init_process(self):
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        super().init_process()

    def init_signals(self):
        # Set up signals through the event loop API.
        loop = asyncio.get_event_loop()
        loop.add_signal_handler(signal.SIGQUIT, self.handle_quit, signal.SIGQUIT, None)
        loop.add_signal_handler(signal.SIGTERM, self.handle_exit, signal.SIGTERM, None)
        loop.add_signal_handler(signal.SIGINT, self.handle_quit, signal.SIGINT, None)
        loop.add_signal_handler(signal.SIGWINCH, self.handle_winch, signal.SIGWINCH, None)
        loop.add_signal_handler(signal.SIGUSR1, self.handle_usr1, signal.SIGUSR1, None)
        loop.add_signal_handler(signal.SIGABRT, self.handle_abort, signal.SIGABRT, None)

        # Don't let SIGTERM and SIGUSR1 disturb active requests
        # by interrupting system calls
        signal.siginterrupt(signal.SIGTERM, False)
        signal.siginterrupt(signal.SIGUSR1, False)


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
        return await next_fn()

    def listen(self, port=8000):
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        loop = asyncio.get_event_loop()
        server = loop.create_server(partial(HttpProtocol, loop=loop, handler=self), port=port)
        loop.create_task(server)
        try:
            print('Listen')
            loop.run_forever()
        except KeyboardInterrupt:
            print('\r', end='\r')
            print('Stoped')
        server.close()
        loop.close()
