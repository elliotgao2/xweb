import random

import multiprocessing
import signal

import webtest

from xweb.application import XWeb


def test_single_app():
    app = XWeb()

    @app.get('/')
    def handler():
        return 'Hello'

    client = webtest.TestApp(app)
    resp = client.get('/')
    assert resp.text == 'Hello'


def test_many_app():
    app1 = XWeb()
    app2 = XWeb()

    @app1.get('/')
    def handler():
        return 'app1'

    @app2.get('/')
    def handler():
        return 'app2'

    client1 = webtest.TestApp(app1)
    client2 = webtest.TestApp(app2)
    resp1 = client1.get('/')
    resp2 = client2.get('/')
    assert resp1.text == 'app1'
    assert resp2.text == 'app2'
