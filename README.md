# xweb

A web framework like Bottle, but less than 500 lines and writen in python

## hello world
```python
from xweb.application import XWeb

app = XWeb()


@app.route('/users/:name')
def hello(name):
    return 'hello {}'.format(name)


app.listen(3000)
```

## request

```python
from xweb.globals import request
from xweb.application import XWeb

app = XWeb()


@app.route('/request/')
def hello():
    request_data = {
        "args":request.args,
        "path":request.path,
        "query_string":request.query_string,
        "query":request.query,
        "files":request.files,
        "form":request.forms
    }
    return request_data


app.listen(3000)
```

## response

## middleware

## TODO

1. choose the necessary request data 
2. design the humanized response structure