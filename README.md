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