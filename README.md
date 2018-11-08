# ![[logo](https://github.com/gaojiuli/xweb)](logo.png)


![[Build](https://travis-ci.org/gaojiuli/xweb)](https://travis-ci.org/gaojiuli/xweb.svg?branch=master)
![[License](https://pypi.python.org/pypi/xweb/)](https://img.shields.io/pypi/l/xweb.svg)
![[Pypi](https://pypi.python.org/pypi/xweb/)](https://img.shields.io/pypi/v/xweb.svg)
![[Python](https://pypi.python.org/pypi/xweb/)](https://img.shields.io/pypi/pyversions/xweb.svg)

High performance web framework.

## Installation

`pip install xweb`

## Usage

```python
from xweb import App, RESTController


class IndexController(RESTController):
    async def get(self):
        self.ctx.body = {"Hello": "World"}


app = App()
app.routes = {
    '/': IndexController
}

app.listen()
```