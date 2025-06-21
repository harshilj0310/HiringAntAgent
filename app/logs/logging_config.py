import logging
import logging.config
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logging(
    log_file: str = "app/logs/app.log",
    log_level: int = logging.INFO,
    console_level: int = logging.INFO,
    max_bytes: int = 5 * 1024 * 1024,  # 5MB
    backup_count: int = 5
):
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": log_file,
                "formatter": "default",
                "level": log_level,
                "maxBytes": max_bytes,
                "backupCount": backup_count,
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": console_level,
            },
        },
        "root": {
            "handlers": ["file", "console"],
            "level": min(log_level, console_level),
        },
    }

    logging.config.dictConfig(logging_config)
