"""python vibora_app.py"""
from vibora import Request, Vibora
from vibora.responses import Response

app = Vibora()


@app.route('/')
async def home(request: Request):
    return Response(b'hello world')


# 90000 Requests/sec
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000, workers=4)
