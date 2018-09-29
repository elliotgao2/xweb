import time
import ujson as json

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
    s = (time.time() - start) * 1000
    ctx['X-Response-Time'] = f'{s:.2f}ms'


@app.use
async def response(ctx):
    # ctx.abort(401, 'access_denied', {"user": "admin"})
    ctx.res.body = json.dumps(ctx.headers)


if __name__ == '__main__':
    app.listen(8000)
