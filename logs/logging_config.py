import logging
import logging.config
from pathlib import Path

def setup_logging(
    log_file: str = "logs/app.log",
    log_level: int = logging.INFO,
    console_level: int = logging.INFO
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
                "class": "logging.FileHandler",
                "filename": '/home/shivam/Intern_Work/HiringAntAgent/scripts/logs/app.log',
                "formatter": "default",
                "level": log_level,
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
