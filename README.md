# xweb

A web framework with very few code.

## feature

1. no dependencies
2. very few code
3. easy to use

## install

`pip install xweb`

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
## test

1. `pip install -r requirement.txt`

2. `pytest`

## TODO


### important:

1. auto-reload
2. more test code
3. rewrite global request and response

### normal:

1. more http status code
2. some necessary middleware 
3. support blueprint
4. a cool logo
