class XWebException(Exception):
    """ A base class for exceptions"""


class RouteError(XWebException):
    """ This is a base class for all routing related exceptions """


class HTTPError(XWebException):
    """ HTTPError """


def abort(status_code):
    raise HTTPError(status_code)
