import os
import logging
from logging.config import dictConfig

from dotenv import load_dotenv

load_dotenv()

console_handler_level = os.getenv('LOGGING_LEVEL', 'INFO')
console_handler_format = os.getenv('LOGGING_FORMAT', 'standard')

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
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
            'stream': 'ext://sys.stdout'
        },
        'file_debug': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'detailed',
            'level': 'DEBUG',
            'filename': 'debug.log',
            'maxBytes': 1024*1024*5,
            'backupCount': 3,
            'encoding': 'utf8',
        },
        'file_error': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'detailed',
            'level': 'ERROR',
            'filename': 'error.log',
            'maxBytes': 1024*1024*5,
            'backupCount': 3,
            'encoding': 'utf8',
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