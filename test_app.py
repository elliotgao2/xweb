from xweb.application import XWeb
from xweb.application import request

app = XWeb()


@app.route('/users/:pk')
def hello(pk):
    return request.query_string + pk


app.listen(3000)
