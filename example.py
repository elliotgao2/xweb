from xweb import App

app = App()
import ujson as json


@app.use
async def logger(ctx, fn):
    await fn()
    # rt = ctx['X-Response-Time']
    # print(rt)


@app.use
async def response_time(ctx, fn):
    # start = time.time()
    await fn()
    # s = (time.time() - start) * 1000
    # ctx['X-Response-Time'] = f'{s:.0f}ms'


@app.use
async def response(ctx):
    ctx.body = json.dumps({"Hello World": 1})


if __name__ == '__main__':
    app.listen(8000)
