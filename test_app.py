from xweb.application import XWeb
from xweb.exception import HTTPError
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


@app.route('/users/:name/')
def hello(name):
    return 'hello {}'.format(name)


@app.route('/requests/')
def requests():
    # request_data = {
    #     "args": request.args,
    #     "url": request.url,
    #     "query_string": request.query_string,
    #     "query": request.query,
    #     "files": request.files,
    #     "form": request.form,
    #     "body": request.body,
    # }
    return request.ip


app.listen(3000)
