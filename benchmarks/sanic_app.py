"""python sanic_app.py"""
from sanic import Sanic
from sanic.response import text

app = Sanic()


@app.route('/')
async def test(request):
    return text('hello world')


# Requests/sec 50000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, workers=4, access_log=False)
