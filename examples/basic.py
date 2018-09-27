from xweb import XWeb

app = XWeb()


class Resource:
    def __call__(self, ctx):
        return "Home"


def index(ctx):
    return "1111"


def home(ctx):
    return "2222"


app.add_route('/', Resource)
app.add_route('/home', home)

app.run()
