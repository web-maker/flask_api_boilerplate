import os


TMP = os.path.expanduser("./tmp/")

bind = "unix:/var/tmp/gunicorn.sock"
workers = 1
worker_class = "gevent"
max_requests = 1000
daemon = False
pidfile = TMP + "api_gunicorn.pid"
accesslog = "logs/api_gunicorn.access.log"
errorlog = "logs/api_gunicorn.error.log"
graceful_timeout = 60
timeout = 300
keepalive = 0
