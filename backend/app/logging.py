import logging
from logging.handlers import RotatingFileHandler
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

def setup_logging(app):
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )

    app.logger.handlers.clear()
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        "app.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
    )
    file_handler.setFormatter(formatter)

    app.logger.setLevel(LOG_LEVEL)
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)

    logging.getLogger("google.ads.googleads").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)