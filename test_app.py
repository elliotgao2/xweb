from xweb.application import XWeb

app = XWeb()


@app.route('/users/:name')
def hello(name):
    return 'hello {}'.format(name)


app.listen(3000)
