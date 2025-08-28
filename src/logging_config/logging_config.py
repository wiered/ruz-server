import os
import logging
from logging.config import dictConfig

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'INFO',
            'stream': 'ext://sys.stdout'
        },
        'console_debug': {
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',
            'level': 'DEBUG',
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
            'handlers': ['console_debug', 'file_debug', 'file_error'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}

if __name__ == '__main__':
    dictConfig(LOGGING_CONFIG)