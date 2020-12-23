import logging
import logging.config

from path import Path

BASE_PATH = Path(__file__).parent.parent
LOGS_PATH = BASE_PATH / 'logs'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(levelname)s:%(name)s: %(message)s (%(asctime)s; %(filename)s:%(lineno)d)',
            'datefmt': "%Y-%m-%d %H:%M:%S",
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'rotate_file_task': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOGS_PATH / 'rotated_task.log'),
            'encoding': 'utf8',
            'maxBytes': 500000,
            'backupCount': 1,
        },
        'rotate_file_celery': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOGS_PATH / 'rotated_celery.log'),
            'encoding': 'utf8',
            'maxBytes': 500000,
            'backupCount': 1,
        },
        'rotate_file_global': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOGS_PATH / 'rotated_global.log'),
            'encoding': 'utf8',
            'maxBytes': 500000,
            'backupCount': 1,
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'rotate_file_global'],
            'level': 'DEBUG',
        },
        'tasks': {
            'handlers': ['console', 'rotate_file_task'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'celery.task': {
            'handlers': ['console', 'rotate_file_celery'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
logging.config.dictConfig(LOGGING)
