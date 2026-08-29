import os

bind = f"{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '5000')}"
workers = int(os.getenv("GUNICORN_WORKERS", "2"))
threads = int(os.getenv("GUNICORN_THREADS", "2"))
timeout = 60
accesslog = "-"
errorlog = "-"
loglevel = "info"
