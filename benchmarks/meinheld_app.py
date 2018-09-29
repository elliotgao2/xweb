"""gunicorn -k meinheld.gmeinheld.MeinheldWorker -w4 meinheld_app:app -b 127.0.0.1:8000"""


# Requests/sec 77000
def app(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [b'Hello world']
