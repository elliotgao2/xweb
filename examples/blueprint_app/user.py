from xweb.blueprint import Blueprint

user = Blueprint('/users/')


@user.route('/')
def user_list():
    return 'hello world111!'
