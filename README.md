# ![[logo](https://github.com/gaojiuli/xweb)](logo.png)


![[Build](https://travis-ci.org/gaojiuli/xweb)](https://travis-ci.org/gaojiuli/xweb.svg?branch=master)
![[License](https://pypi.python.org/pypi/xweb/)](https://img.shields.io/pypi/l/xweb.svg)
![[Pypi](https://pypi.python.org/pypi/xweb/)](https://img.shields.io/pypi/v/xweb.svg)
![[Python](https://pypi.python.org/pypi/xweb/)](https://img.shields.io/pypi/pyversions/xweb.svg)

## Why use xweb

Your learning costs will be very low .
Your code will be elegant.
Your bug will be easy to solve.
Your life will be long.

- Xweb is easy to use. 
- Xweb has very simple api. 
- Xweb needn't any third-party dependency.
- Xweb does not have any redundant code for python2.
- Source code is easy to understand.
- It is easy to write xweb's middleware. 

## Installation

`pip install xweb`

## Hello world
```python
from xweb.application import XWeb

app = XWeb()


@app.route('/')
def hello():
    return 'hello world!'


app.listen(3000)
```

## Route

```python
from xweb.application import XWeb

app = XWeb()

@app.route('/:name/',methods=['GET','POST'])
def call_my_name(name):
    return 'hi {}!'.format(name)
    
@app.post('/post/')
def post():
    return 'hi post!'
    
@app.get('/:name/')
def get():
    return 'hi get!'

@app.put('/put/')
def put():
    return 'hi put!'

@app.patch('/patch/')
def patch():
    return 'hi patch!'

@app.delete('/delete/')
def delete():
    return 'hi delete!'
    

app.listen(3000)
```

## Request

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
request.host
request.protocol
request.body
request.content_type
request.content_length

```


## Response

```python
from xweb.globals import response

response.headers
response.status
response.body
```

## Middleware

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

## Exception

```python
from xweb.application import XWeb
from xweb.exception import abort
from xweb.globals import response

app = XWeb()

@app.route('/')
def hello():
    abort(500)
    return 'OK'
    
@app.exception(500)
def hello():
    response.body = "Something wrong"

app.listen(3000)
```


## Test

1. `pip install -r requirement.txt`

2. `pytest`

## How to contribute

1. star
2. fork
3. add your code
4. add test code and run test
5. pull request

## TODO


### important:

1. auto-reload
2. a cool logo
3. documentation

### normal:

1. more test code
2. more necessary request arguments
3. more http status code
4. more necessary middleware 
5. support blueprints

