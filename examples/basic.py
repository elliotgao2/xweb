from xweb.application import XWeb
from xweb.exception import abort
from xweb.globals import request, response

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


@app.route('/', methods=['GET', 'POST'])
def hello():
    return '<h1>hello world</h1>'


@app.route('/environ')
def environ():
    return str(request.environ)


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


@app.get('/exception')
def post():
    abort(500)
    return "OK"


@app.exception(500)
def exception():
    response.body = "FAIL"

app.listen(3000)
