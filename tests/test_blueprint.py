import webtest

def test_blueprint():
    from xweb.application import XWeb
    from xweb.blueprint import Blueprint

    user = Blueprint('/users/')

    @user.route('/')
    def user_list():
        return 'user'

    app = XWeb()

    @app.route('/')
    def hello():
        return 'app'

    app.register_blueprint(user)

    client = webtest.TestApp(app)
    assert client.get('/').text == 'app'
    assert client.get('/users/').text == 'user'