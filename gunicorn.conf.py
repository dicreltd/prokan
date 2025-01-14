# gunicorn.conf.py
workers = 3
bind = "0.0.0.0:8885"
timeout = 120
accesslog = "-"
errorlog = "-"
worker_class = "sync"
