import asyncio
import logging
import ujson as json
from http import HTTPStatus

import httptools

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
data = json.dumps({"b": 1})
response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(data)}\r\n\r\n{data}".encode()


class Response:
    def __init__(self, body=None, headers=None, status_code=HTTPStatus.OK):
        self.status_code = status_code
        if self.status_code.value >= 300:
            self.body = body or self.status_code.phrase
        base_header = {'Content-Type': 'text/plain', "Content-Length": len(self.body)}
        self.headers = headers and base_header.update(base_header) or base_header

    def __str__(self):
        status_str = f'{self.status_code} {self.status_code.phrase}'
        header_str = '\r\n'.join([f'{k}: {v}' for k, v in self.headers.items()])
        return f'HTTP/1.1 {status_str}\r\n{header_str}\r\n\r\n{self.body}'

    def to_bytes(self):
        return self.__str__().encode()


response_404 = Response(status_code=HTTPStatus.NOT_FOUND).to_bytes()
response_500 = Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR).to_bytes()


class Request:
    def __init__(self, path="", query="", schema="", body="", url=''):
        self.body = body
        self.schema = schema
        self.query = query
        self.path = path
        self.headers = {}
        self.method = 'HEAD'
        self.url = url
        self.ip = ''


class ServerProtocol(asyncio.Protocol):
    route = {}

    def __init__(self):
        self.parser = None
        self.transport = None
        self.request = Request()

    def connection_made(self, transport):
        self.parser = httptools.HttpRequestParser(self)
        self.transport = transport
        addr = transport.get_extra_info('peername')
        self.request.ip = addr[0]

    def on_body(self, body):
        self.request.body = body

    def on_header(self, name, value):
        self.request.headers[name] = value

    def on_message_complete(self):
        logging.info(f'{self.request.ip} {self.request.method} {self.request.url}')
        self.transport.write(response_404)

    def on_url(self, url):
        parsed_url = httptools.parse_url(url)
        self.request.url = url
        self.request.path = parsed_url.path
        self.request.query = parsed_url.query
        self.request.method = self.parser.get_method()

    def data_received(self, data):
        self.parser.feed_data(data)

    def eof_received(self):
        self.transport.close()

    def connection_lost(self, exc):
        self.transport.close()


class App:
    def add_route(self, path, handler):
        ServerProtocol.route[path.encode()] = handler

    def run(self, ip: str = "127.0.0.1", port: int = 8888, debug=False):
        logger.setLevel(debug and logging.DEBUG or logging.ERROR)
        loop = asyncio.get_event_loop()
        ServerProtocol.ip = ip
        ServerProtocol.port = port
        coro = loop.create_server(ServerProtocol, ip, port)
        server = loop.run_until_complete(coro)
        logger.info(f"Serving on http://{ip}:{port}")
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            print('', end='\r')
            logger.info(f"Server closing!")

        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()
