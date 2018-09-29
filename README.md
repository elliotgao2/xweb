# ![[logo](https://github.com/gaojiuli/xweb)](logo.png)


![[Build](https://travis-ci.org/gaojiuli/xweb)](https://travis-ci.org/gaojiuli/xweb.svg?branch=master)
![[License](https://pypi.python.org/pypi/xweb/)](https://img.shields.io/pypi/l/xweb.svg)
![[Pypi](https://pypi.python.org/pypi/xweb/)](https://img.shields.io/pypi/v/xweb.svg)
![[Python](https://pypi.python.org/pypi/xweb/)](https://img.shields.io/pypi/pyversions/xweb.svg)

High performance web framework built with uvloop and httptools

In Xweb, everything is asynchronous.

## Features

1. High performarce
2.

## Requirements

1. Python3.6+

## Installation

`pip install xweb`

## Get Started

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
    s = (time.time() - start) * 1000_000
    ctx['X-Response-Time'] = f'{s:.0f}µs'


@app.use
async def response(ctx):
    ctx.res.body = "Hello World"


if __name__ == '__main__':
    app.listen(8000)
```

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

## Dev

`python app.py`

## Deploy

`gunicorn -w 4 -k xweb.XWebWorker app:app`

## Test

1. `pip install -r requirement.txt`
2. `pytest --cov xweb.py`

