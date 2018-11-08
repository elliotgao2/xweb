from xweb import App, Model, RESTController


class UserModel(Model):
    schema = {
        "type": "object",
        "properties": {
            "username": {"type": "string"},
            "password": {"type": "string"},
        },
        "required": ['username']
    }


class EventController(RESTController):
    async def get(self):
        Model.validate(self.ctx.json)
        self.ctx.body = {"Hello": "World"}


app = App()
app.routes = {
    '/': EventController
}

app.listen()
