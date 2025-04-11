import os
import logging.config
from django.conf import settings

def configure_logging():
    """
    Configure the logging system for the application.
    This sets up different handlers based on the environment.
    """
    # Ensure log directory exists
    # Use BASE_DIR from settings if available, otherwise use a relative path
    if hasattr(settings, 'BASE_DIR'):
        log_dir = os.path.join(settings.BASE_DIR, 'logs')
    else:
        # Fallback to a directory relative to this file
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    
    os.makedirs(log_dir, exist_ok=True)
    
    # Define logging configuration
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{asctime} {levelname} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
            'json': {
                'format': '{"time": "%(asctime)s", "level": "%(levelname)s", "module": "%(module)s", "message": "%(message)s"}',
                'style': '%',
            },
        },
        'filters': {
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            },
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse',
            },
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'filters': ['require_debug_true'],
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
            'file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(log_dir, 'gitako.log'),
                'maxBytes': 10 * 1024 * 1024,  # 10 MB
                'backupCount': 10,
                'formatter': 'verbose',
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(log_dir, 'error.log'),
                'maxBytes': 10 * 1024 * 1024,  # 10 MB
                'backupCount': 10,
                'formatter': 'verbose',
            },
            'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler',
                'formatter': 'verbose',
            },
            'json_file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(log_dir, 'gitako.json'),
                'maxBytes': 10 * 1024 * 1024,  # 10 MB
                'backupCount': 10,
                'formatter': 'json',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'file', 'mail_admins'],
                'level': 'INFO',
                'propagate': True,
            },
            'django.server': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False,
            },
            'django.request': {
                'handlers': ['error_file', 'mail_admins'],
                'level': 'ERROR',
                'propagate': False,
            },
            'django.db.backends': {
                'handlers': ['console', 'error_file'],
                'level': 'ERROR',
                'propagate': False,
            },
            'gitako': {
                'handlers': ['console', 'file', 'error_file', 'json_file'],
                'level': 'INFO',
                'propagate': False,
            },
            'gitako.api': {
                'handlers': ['console', 'file', 'error_file', 'json_file'],
                'level': 'INFO',
                'propagate': False,
            },
            'gitako.background': {
                'handlers': ['console', 'file', 'error_file'],
                'level': 'INFO',
                'propagate': False,
            },
            'gitako.security': {
                'handlers': ['console', 'file', 'error_file', 'mail_admins'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    }
    
    # Apply configuration
    logging.config.dictConfig(LOGGING)
    
    return LOGGING