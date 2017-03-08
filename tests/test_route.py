import pytest
import webtest

from xweb.application import XWeb
from xweb.exception import RouteError
from xweb.globals import request


def test_get():
    app = XWeb()

    @app.get('/get')
    def handler():
        return 'OK'

    client = webtest.TestApp(app)
    response = client.get('/get')
    assert response.text == 'OK'
    assert response.status_int == 200

    response = client.post('/get', expect_errors=True)
    assert response.status_int == 405


def test_slash():
    app = XWeb()

    @app.get('/get')
    def handler():
        return 'OK'

    client = webtest.TestApp(app)

    response = client.get('/get')
    assert response.text == 'OK'

    response = client.get('/get/')
    assert response.text == 'OK'


def test_post():
    app = XWeb()

    @app.post('/post')
    def handler():
        return request.forms

    client = webtest.TestApp(app)
    response = client.post('/post', params={"name": "xweb"})
    assert response.status_int == 200

    response = client.get('/post', expect_errors=True)
    assert response.status_int == 405


def test_put():
    app = XWeb()

    @app.put('/put')
    def handler():
        return 'OK'

    client = webtest.TestApp(app)
    response = client.put('/put')
    assert response.text == 'OK'

    response = client.get('/put', expect_errors=True)
    assert response.status_int == 405


def test_patch():
    app = XWeb()

    @app.put('/patch')
    def handler():
        return 'OK'

    client = webtest.TestApp(app)
    response = client.put('/patch')
    assert response.text == 'OK'

    response = client.get('/patch', expect_errors=True)
    assert response.status_int == 405


def test_head():
    app = XWeb()

    @app.put('/head')
    def handler():
        return 'OK'

    client = webtest.TestApp(app)
    response = client.put('/head')
    assert response.text == 'OK'

    response = client.get('/head', expect_errors=True)
    assert response.status_int == 405


def test_option():
    app = XWeb()

    @app.put('/option')
    def handler():
        return 'OK'

    client = webtest.TestApp(app)
    response = client.put('/option')
    assert response.text == 'OK'

    response = client.get('/option', expect_errors=True)
    assert response.status_int == 405


def test_static_routes():
    app = XWeb()

    @app.route('/test')
    def handler1():
        return 'OK1'

    @app.route('/pizazz')
    def handler2():
        return 'OK2'

    client = webtest.TestApp(app)
    response = client.get('/test')
    assert response.text == 'OK1'

    response = client.get('/pizazz')
    assert response.text == 'OK2'


def test_dynamic_route():
    app = XWeb()

    results = []

    @app.route('/folder/:name/:age')
    def handler(name, age):
        results.append(name)
        results.append(age)
        return 'OK'

    client = webtest.TestApp(app)
    response = client.get('/folder/test123/23')
    assert response.text == 'OK'
    assert results[0] == 'test123'
    assert results[1] == '23'


def test_route_duplicate():
    app = XWeb()

    with pytest.raises(RouteError):
        @app.route('/test')
        def handler1():
            pass

        @app.route('/test')
        def handler2():
            pass

    with pytest.raises(RouteError):
        @app.route('/test/:dynamic/')
        def handler1():
            pass

        @app.route('/test/:dynamic/')
        def handler2():
            pass
