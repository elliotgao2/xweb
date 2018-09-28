import time

from xweb import App

app = App()


@app.use
async def logger(req, res, fn):
    await fn()
    rt = res['X-Response-Time']
    print(rt)


@app.use
async def response_time(req, res, fn):
    start = time.time()
    await fn()
    s = time.time() - start
    res['X-Response-Time'] = f'{s:.2f}s'


@app.use
async def response(req, res):
    res.body = "Hello World!"
