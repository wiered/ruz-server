import os
import logging
import re
from logging.config import dictConfig

from ruz_server.settings import ROOT, settings

console_handler_level = settings.logging_level
console_handler_format = settings.logging_format
LOGS_DIR = ROOT / "logs"
os.makedirs(LOGS_DIR, exist_ok=True)


class SecretMaskingFilter(logging.Filter):
    """
    Маскирует секреты в connection strings и query-параметрах.

    Цель: гарантировать, что в логах не окажутся пароли/токены,
    даже если они попадут внутрь строки сообщения.
    """

    # postgres://user:pass@host:port/db
    _uri_credentials_re = re.compile(r"://([^:/\s]+):([^@\s]+)@")
    # ...?password=...&...
    _query_secret_re = re.compile(r"(?i)\b(password|pass|pwd|token)\b=([^&\s]+)")

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            msg = record.getMessage()
        except Exception:
            return True

        masked = self._uri_credentials_re.sub(r"://\1:***@", msg)
        masked = self._query_secret_re.sub(lambda m: f"{m.group(1)}=***", masked)

        if masked != msg:
            # Изменяем сообщение в самом record, чтобы caplog/другие handlers
            # увидели уже замаскированный текст.
            record.msg = masked
            record.args = ()

        return True


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'secret_masking': {
            '()': 'ruz_server.logging_config.logging_config.SecretMaskingFilter',
        }
    },
    'formatters': {
        'standard': {
            'format': '%(levelname)s: %(asctime)s %(name)s - %(message)s'
        },
        'detailed': {
            'format': '%(levelname)s: %(asctime)s %(name)s (%(filename)s:%(lineno)d) - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': console_handler_format,
            'level': console_handler_level,
            'stream': 'ext://sys.stdout',
            'filters': ['secret_masking'],
        },
        'file_debug': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'detailed',
            'level': 'DEBUG',
            'filename': str(LOGS_DIR / 'debug.log'),
            'maxBytes': 1024*1024*5,
            'backupCount': 3,
            'encoding': 'utf8',
            'filters': ['secret_masking'],
        },
        'file_error': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'detailed',
            'level': 'ERROR',
            'filename': str(LOGS_DIR / 'error.log'),
            'maxBytes': 1024*1024*5,
            'backupCount': 3,
            'encoding': 'utf8',
            'filters': ['secret_masking'],
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file_debug', 'file_error'],
            'level': 'DEBUG',
            'propagate': False
        },
        'sqlalchemy.engine': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False
        }
    }
}

class ColoredFormatter(logging.Formatter):
    green = "\033[0;32m"
    yellow = "\033[1;33m"
    red = "\033[1;31m"
    purple = "\033[0;35m"
    reset = "\033[0m"

    colors = {
        logging.INFO: green,
        logging.WARNING: yellow,
        logging.ERROR: red,
        logging.DEBUG: purple,
    }

    def format(self, record):
        message = super().format(record)
        color = self.colors.get(record.levelno, "")
        if color:
            levelname = f"{record.levelname}"
            colored_level = f"{color}{levelname}{self.reset}"
            message = message.replace(levelname, colored_level)
        return message

if __name__ == '__main__':
    dictConfig(LOGGING_CONFIG)