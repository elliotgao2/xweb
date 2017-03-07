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

## middleware

## TODO

1. more http status code
2. some necessary middleware 
3. enough test code
