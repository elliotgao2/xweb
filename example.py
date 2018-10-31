from jsonschema import Draft4Validator, ErrorTree

from xweb import App, HTTPException, RESTController


class Model:
    schema = {
        "type": "object",
        "properties": {
            "username": {"type": "string"},
            "password": {"type": "string"},
        },
        "required": ['username']
    }

    @classmethod
    def validate(cls):
        errors = ErrorTree(Draft4Validator(cls.schema).iter_errors({"name": "Eggs", "price": 34.99})).errors
        if errors:
            raise HTTPException(400, msg=str(errors))


class EventController(RESTController):
    async def get(self):
        Model.validate()
        self.ctx.body = "222"


app = App()
app.routes = {
    '/': EventController
}

app.listen()
