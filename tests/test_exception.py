import webtest

from xweb.application import XWeb
from xweb.exception import abort
from xweb.globals import response


def test_exception():
    app = XWeb()

    @app.get('/exception')
    def post():
        abort(500)
        return "OK"

    @app.exception(500)
    def exception():
        response.body = "FAIL"

    client = webtest.TestApp(app)
    resp = client.get('/exception', expect_errors=True)
    assert resp.text == "FAIL"


def test_middleware_exception():
    app = XWeb()

    @app.middleware('request')
    def request_abort():
        abort(405)
        return "OK"

    @app.get('/')
    def request_abort():
        return "OK"

    @app.exception(405)
    def exception():
        response.body = "FAIL"

    client = webtest.TestApp(app)
    resp = client.get('/', expect_errors=True)
    assert resp.text == "FAIL"


def test_404_exception():
    app = XWeb()

    @app.get('/')
    def request_abort():
        return "OK"

    @app.exception(404)
    def exception():
        response.body = "FAIL"

    client = webtest.TestApp(app)
    resp = client.get('/')
    assert resp.text == "OK"

    resp = client.get('/no', expect_errors=True)
    assert resp.text == "FAIL"
