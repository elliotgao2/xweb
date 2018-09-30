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
    ctx.body = "Hello World"


if __name__ == '__main__':
    app.listen(8000)
