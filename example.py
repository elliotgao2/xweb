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
    ctx.body = "11ddd11"
