from xweb.application import XWeb
from xweb.globals import request

app = XWeb()


@app.middleware('request')
def print_on_request1():
    print("I print when a request is received by the server1")


@app.middleware('request')
def print_on_request2():
    print("I print when a request is received by the server2")


@app.middleware('response')
def print_on_response1():
    print("I print when a response is returned by the server1")


@app.middleware('response')
def print_on_response2():
    print("I print when a response is returned by the server2")


@app.route('/')
def hello():
    return 'hello world!'


@app.route('/headers/')
def headers():
    return request.headers.store


@app.route('/forms/', methods=['POST'])
def forms():
    return request.forms


@app.route('/query/')
def query():
    return request.query


@app.post('/post')
def post():
    return request.forms


@app.post('/exception')
def post():
    return request.forms


app.listen(3000)
