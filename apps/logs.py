import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logs(app):
    logdir = app.config.get("APP_LOGDIR", "./logs/")
    if not os.path.exists(logdir):
        os.mkdir(logdir)
    formatter = logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d}"
        "%(levelname)s - %(message)s",
    )
    handler = RotatingFileHandler(
        app.config.get("APP_LOGFILE"), mode="w",
        maxBytes=10000000, backupCount=5,
    )
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
