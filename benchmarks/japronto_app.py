"""python japronto_app.py"""
from japronto import Application


def hello(request):
    return request.Response(text='Hello world!')


# 150000
app = Application()
app.router.add_route('/', hello)
app.run(debug=False, worker_num=4, port=8000)
