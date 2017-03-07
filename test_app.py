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
    return request.headers


@app.route('/requests/', methods=['POST'])
def requests():
    return request.headers


app.listen(3000)
