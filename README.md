# xweb

A web framework less than 500 lines

## hello world
```python
from xweb.application import XWeb

app = XWeb()


@app.route('/')
def hello():
    return 'hello world!'


app.listen(3000)
```

## route
```python
from xweb.application import XWeb

app = XWeb()


@app.route('/:name/')
def call_my_name(name):
    return 'hi {}!'.format(name)


app.listen(3000)
```

## request

```python
from xweb.globals import request

request.path
request.query_string
request.query
request.files
request.forms
request.json
request.ip
request.hostname
request.headers

```


## response

```python
from xweb.globals import response

response.headers
response.status
response.body
```

## middleware

```python
from xweb.application import XWeb

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

@app.route('/:name/')
def call_my_name(name):
    return 'hi {}!'.format(name)


app.listen(3000)
```

## TODO

1. more http status code
2. some necessary middleware 
3. enough test code
4. support blueprint
