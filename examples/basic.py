from xweb import XWeb

app = XWeb()


def index(ctx):
    return "1111"


def home(ctx):
    return "2222"


app.add_route('/', index)
app.add_route('/home', home)

app.run()
