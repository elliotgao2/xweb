# ![[logo](https://github.com/gaojiuli/xweb)](logo.png)


![[Build](https://travis-ci.org/gaojiuli/xweb)](https://travis-ci.org/gaojiuli/xweb.svg?branch=master)
![[License](https://pypi.python.org/pypi/xweb/)](https://img.shields.io/pypi/l/xweb.svg)
![[Pypi](https://pypi.python.org/pypi/xweb/)](https://img.shields.io/pypi/v/xweb.svg)
![[Python](https://pypi.python.org/pypi/xweb/)](https://img.shields.io/pypi/pyversions/xweb.svg)

Expressive middleware for using async functions. Inspired by [koa](https://github.com/koajs/koa).

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
    rt = getattr(ctx, 'X-Response-Time')


@app.use
async def response_time(ctx, fn):
    start = time.time()
    await fn()
    s = time.time() - start
    setattr(ctx, 'X-Response-Time', f'{s:.2f}s')


@app.use
async def response(ctx):
    ctx.body = "Hello World!"
```

## Run and Deploy

`gunicorn -w 4 -k xweb.XWebWorker app:app`

## Test

1. `pip install -r requirement.txt`
2. `pytest --cov xweb.py`

