"""gunicorn -w4 -k xweb.XWebWorker xweb_app:app"""
from xweb import App

app = App()


# 100000 Requests/sec
@app.use
async def response(ctx):
    ctx.res.body = "Hello World"
