import webtest

from xweb.application import XWeb
from xweb.globals import response


def test_get():
    app = XWeb()

    @app.get('/')
    def handler():
        return 'Hello'

    client = webtest.TestApp(app)
    response = client.get('/')
    assert response.text == 'Hello'


def test_headers():
    app = XWeb()

    @app.route('/')
    def handler():
        response.headers["spam"] = "great"
        return 'Hello'

    client = webtest.TestApp(app)
    resp = client.get('/')

    assert resp.headers.get('spam') == 'great'
