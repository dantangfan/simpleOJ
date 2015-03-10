from application import app
from gevent.wsgi import WSGIServer
import sys
print 'server runing...'


import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app.run(debug=True)

"""
http_server = WSGIServer(('', 500), app)
http_server.serve_forever()
"""