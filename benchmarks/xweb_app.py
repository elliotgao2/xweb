"""python xweb_app.py"""
from xweb import App

app = App()


# 100000 Requests/sec
@app.use
async def response(ctx):
    ctx.body = "Hello World"


app.listen(8000)
