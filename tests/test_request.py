import json

import webtest

from xweb.application import XWeb
from xweb.exception import HTTPError
from xweb.globals import response, request


def test_get():
    app = XWeb()

    @app.get('/')
    def handler():
        return 'Hello'

    client = webtest.TestApp(app)
    resp = client.get('/')
    assert resp.text == 'Hello'


def test_headers():
    app = XWeb()

    @app.route('/')
    def handler():
        response.headers["spam"] = "great"
        return 'Hello'

    client = webtest.TestApp(app)
    resp = client.get('/')
    assert resp.headers.get('spam') == 'great'


def test_non_str_headers():
    app = XWeb()

    @app.route('/')
    def handler():
        response.headers["answer"] = 42
        return 'Hello'

    client = webtest.TestApp(app)
    resp = client.get('/')
    assert resp.headers.get('answer') == '42'


def test_invalid_response():
    app = XWeb()

    @app.route('/')
    def handler():
        raise HTTPError(500)

    client = webtest.TestApp(app)
    resp = client.get('/', expect_errors=True)
    assert resp.status_int == 500
    assert resp.text == "Internal Server Error"


def test_json():
    app = XWeb()

    @app.route('/')
    def handler():
        return {"test": True}

    client = webtest.TestApp(app)
    resp = client.get('/')
    try:
        results = json.loads(resp.text)
    except:
        raise ValueError("Expected JSON response but got '{}'".format(response))

    assert results.get('test') == True


def test_invalid_json():
    app = XWeb()

    @app.post('/')
    def handler():
        return request.json

    client = webtest.TestApp(app)
    resp = client.post('/', params="dasdas")
    assert resp.text == '{}'


def test_post_json():
    app = XWeb()

    @app.route('/', methods=['POST'])
    def handler():
        return request.json

    payload = {'test': 'OK'}
    headers = {'content-type': 'application/json'}
    client = webtest.TestApp(app)
    resp = client.post_json('/', params=payload, headers=headers)
    assert resp.json.get('test') == 'OK'


def test_post_form_urlencoded():
    app = XWeb()

    @app.route('/', methods=['POST'])
    def handler():
        return request.forms

    payload = {'test': 'OK'}
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    client = webtest.TestApp(app)
    resp = client.post('/', params=payload, headers=headers)
    assert resp.json.get('test') == 'OK'


def test_post_form_multipart_form_data():
    app = XWeb()

    @app.route('/', methods=['POST'])
    def handler():
        return request.forms

    payload = '------xweb\r\n' \
              'Content-Disposition: form-data; name="test"\r\n' \
              '\r\n' \
              'fuck\r\n' \
              '------xweb--\r\n'
    headers = {'content-type': 'multipart/form-data; boundary=----xweb'}
    client = webtest.TestApp(app)
    resp = client.post('/', params=payload, headers=headers)
    assert resp.json.get('test') == 'fuck'


def test_query():
    app = XWeb()

    @app.get('/query')
    def query():
        return request.query

    client = webtest.TestApp(app)
    resp = client.get('/query/?a=1')
    assert resp.json.get('a') == '1'


def test_files():
    app = XWeb()

    @app.post('/files')
    def files():
        return request.files

    client = webtest.TestApp(app)
    resp = client.post('/files')
    assert resp.text == '{}'
