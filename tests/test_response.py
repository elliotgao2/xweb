import json
from random import choice

import webtest

from xweb.application import XWeb
from xweb.globals import response


def test_response_body_not_a_string():
    app = XWeb()

    random_num = choice(range(1000))

    @app.route('/hello')
    def hello_route():
        return random_num

    client = webtest.TestApp(app)
    resp = client.get('/hello')
    assert resp.text == str(random_num)


def test_response_string():
    app = XWeb()

    @app.route('/hello')
    def hello_route():
        return "hello"

    client = webtest.TestApp(app)
    resp = client.get('/hello')
    assert resp.text == "hello"


def test_response_dict():
    app = XWeb()

    @app.route('/hello')
    def hello_route():
        return {'name': 'xweb'}

    client = webtest.TestApp(app)
    resp = client.get('/hello')
    assert resp.text == json.dumps({'name': 'xweb'})


def test_response_header():
    app = XWeb()

    @app.route('/hello')
    def hello_route():
        response.headers['spam'] = '1'
        return {'name': 'xweb'}

    client = webtest.TestApp(app)
    resp = client.get('/hello')
    assert resp.headers.get('spam') == '1'
