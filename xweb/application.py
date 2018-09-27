import asyncio
import ujson as json

import httptools
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
data = json.dumps({"b": 1})
response_405 = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(data)}\r\n\r\n{data}".encode()
loop = asyncio.get_event_loop()


class Context:
    """"""
    headers = {}


class ServerProtocol(asyncio.Protocol):
    route = {}

    def __init__(self):
        self.parser = None
        self.transport = None
        self.body = b""
        self.header = {}
        self.url = b""
        self.ctx = Context()

    def connection_made(self, transport):
        self.parser = httptools.HttpRequestParser(self)
        self.transport = transport

    def on_body(self, data):
        self.body += data

    def on_header(self, name, value):
        # self.ctx.headers[name] = value
        pass

    def on_message_complete(self):
        if self.url.path not in self.route:
            self.transport.write(response_405)
        else:
            handler = self.route[self.url.path]
            if isinstance(handler, type):
                handler = handler()
            data = handler(self.ctx)
            response = f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(data)}\r\n\r\n{data}'.encode()
            self.transport.write(response)
        return True

    def on_url(self, url):
        self.url = httptools.parse_url(url)

    def data_received(self, data):
        self.parser.feed_data(data)

    def eof_received(self):
        self.transport.close()

    def connection_lost(self, exc):
        self.transport.close()


class XWeb:
    def add_route(self, path, handler):
        ServerProtocol.route[path.encode()] = handler

    def run(self, ip: str = "127.0.0.1", port: int = 8888):
        loop = asyncio.get_event_loop()
        coro = loop.create_server(ServerProtocol, ip, port)
        server = loop.run_until_complete(coro)

        print(f"Serving on http://{ip}:{port}")
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass

        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()
