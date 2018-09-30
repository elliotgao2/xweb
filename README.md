# ![[logo](https://github.com/gaojiuli/xweb)](logo.png)


![[Build](https://travis-ci.org/gaojiuli/xweb)](https://travis-ci.org/gaojiuli/xweb.svg?branch=master)
![[License](https://pypi.python.org/pypi/xweb/)](https://img.shields.io/pypi/l/xweb.svg)
![[Pypi](https://pypi.python.org/pypi/xweb/)](https://img.shields.io/pypi/v/xweb.svg)
![[Python](https://pypi.python.org/pypi/xweb/)](https://img.shields.io/pypi/pyversions/xweb.svg)

High performance web framework built with uvloop and httptools

In Xweb, everything is asynchronous.

## Features

-  High performance.
-  Asynchronous.
-  Small.

## Requirements

- Python3.6+

## Installation

`pip install xweb`

## Get Started

### Hello World

```python
from xweb import App

app = App()

@app.use
async def response(ctx):
    ctx.res.body = "Hello World"


if __name__ == '__main__':
    app.listen(8000)
```

### Example with middleware.

A middleware is an async function or an async callable object which looks like: `async def logger(ctx, fn)`

```python
# app.py

import time

from xweb import App

app = App()


@app.use
async def logger(ctx, fn):
    await fn()
    rt = ctx['X-Response-Time']
    print(rt)


@app.use
async def response_time(ctx, fn):
    start = time.time()
    await fn()
    usage = (time.time() - start) * 1000_000
    ctx['X-Response-Time'] = f'{usage:.0f}µs'


@app.use
async def response(ctx):
    ctx.res.body = "Hello World"


if __name__ == '__main__':
    app.listen(8000)
```

## App

- app.use(fn)
- app.listen(host='127.0.0.1', port=8000, debug=True)

## Context

- ctx.req
- ctx.res
- ctx.send
- ctx.abort(self, status, msg="", properties="")
- ctx.check(self, value, status=400, msg='', properties="")

### Request
    
`ctx.req` is a Request object.

- ctx.req.headers dict
- ctx.req.method str
- ctx.req.url str
- ctx.req.raw bytes
- ctx.req.ip str

### Response

`ctx.res` is a Request object.

- ctx.res.body str
- ctx.res.status int
- ctx.res.msg str
- ctx.res.headers dict



## Benchmark

- Benchmark code in benchmarks/.
- environment: `iMac (Retina 4K, 21.5-inch, 2017)`, `3 GHz Intel Core i5`, `8 GB 2400 MHz DDR4`
- test command: `wrk http://127.0.0.1:8000/ -c 100 -t 10 -d 10 -T 10`

Frameworks| Requests/Sec | Version
-----|-----|-----
xweb|100000|0.1.1
vibora|90000|0.0.6
meinheld + wsgi|77000|0.6.1
sanic|50000|0.7.0

## Deploy and Run

`python app.py`.

## Test

1. `pip install -r requirement.txt`
2. `pytest --cov xweb.py`

## Contributing


### Build Middleware.

XWeb is inspired by [koajs](https://koajs.com/). I need some help for writing middleware as in koa. For example:

1. Body parser. Convert the raw bytes body into dict or file.
2. Data validator. Async data validator with high performance.
3. Router. High performance router like koa-router.
4. etc..

### Open issue.

1. Suggestion.
2. Bug.