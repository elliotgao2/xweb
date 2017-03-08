import webtest

from xweb.application import XWeb
from xweb.globals import request, response


def test_middleware_request():
    app = XWeb()
    results = []

    @app.middleware('request')
    def handler():
        results.append(request)

    @app.route('/hello')
    def hello_route():
        return 'OK'

    client = webtest.TestApp(app)

    resp = client.get('/hello')
    assert resp.text == 'OK'
    assert results[0] is request


def test_middleware_response():
    app = XWeb()
    results = []

    @app.middleware('request')
    def process_response():
        results.append(request)

    @app.middleware('response')
    def process_response():
        results.append(request)
        results.append(response)

    @app.route('/hello')
    def hello_route():
        return 'OK'

    client = webtest.TestApp(app)

    resp = client.get('/hello')
    assert resp.text == 'OK'
    assert results[0] is request
    assert results[1] is request
    assert results[2] is response


def test_middleware_override_request():
    app = XWeb()

    @app.middleware('request')
    def process_response():
        return 'OK'

    @app.route('/hello')
    def hello_route():
        return 'FAIL'

    client = webtest.TestApp(app)

    resp = client.get('/hello')
    assert resp.text == 'OK'


def test_middleware_override_response():
    app = XWeb()

    @app.middleware('response')
    def process_response():
        return 'OK'

    @app.route('/hello')
    def hello_route():
        return 'FAIL'

    client = webtest.TestApp(app)

    resp = client.get('/hello')
    assert resp.text == 'OK'


def test_middleware_order():
    app = XWeb()

    order = []

    @app.middleware('request')
    def request1():
        order.append(1)

    @app.middleware('request')
    def request2():
        order.append(2)

    @app.middleware('request')
    def request3():
        order.append(3)

    @app.middleware('response')
    def response1():
        order.append(4)

    @app.middleware('response')
    def response2():
        order.append(5)

    @app.middleware('response')
    def response3():
        order.append(6)

    @app.route('/hello')
    def handler():
        return 'OK'

    client = webtest.TestApp(app)
    resp = client.get('/hello')

    assert resp.status_int == 200
    assert order == [1, 2, 3, 4, 5, 6]
