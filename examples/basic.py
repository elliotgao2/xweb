from xweb import App

app = App()
# def home(ctx):
#     return "Home"
#
#
# app.add_route('/', home)
app.run(debug=True, ip='0.0.0.0')
