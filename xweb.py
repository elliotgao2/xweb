import asyncio
import signal
from functools import partial

import httptools
import uvloop
from gunicorn.workers.base import Worker

__version__ = '0.1.0'
__author__ = 'gaojiuli'


class Request:
    """Todo"""


class Response:
    """Todo"""

    def __init__(self):
        pass

    def get(self, key):
        return getattr(self, key)


class Context:
    """Todo
    req
    res
    app
    throw
    assert
    respond
    """

    def __init__(self):
        self.body = "a"
        self.req = Request()
        self.res = Response()

    def set(self, key, value):
        print(1111)
        setattr(self.res, key, value)

    def respond(self):
        pass

    def throw(self):
        pass

    def assert_true(self):
        pass


class HttpProtocol(asyncio.Protocol):

    def __init__(self, app, loop):
        self.parser = None
        self.transport = None
        self.handler = app.callable
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
        self.body = body

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
        [loop.create_task(loop.create_server(partial(HttpProtocol, loop=loop, app=self.app), sock=sock))
         for sock in self.sockets]
        loop.run_forever()

    def init_process(self):
        asyncio.get_event_loop().close()
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
        self.handle = None

    def use(self, fn):
        self.handlers.append(fn)

    async def __call__(self, ctx):
        next_fn = None
        handlers = []
        for handler in self.handlers[::-1]:
            if next_fn is not None:
                handler = partial(handler, ctx=ctx, fn=next_fn)
                handlers.append(handler)
            else:
                self.handle = partial(handler, ctx=ctx)
            next_fn = handler
        return await self.handle()
