from user import user
from xweb.application import XWeb

app = XWeb()


@app.route('/')
def hello():
    return 'hello world!'


app.register_blueprint(user)
app.listen(3000)
