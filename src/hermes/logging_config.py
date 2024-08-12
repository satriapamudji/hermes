import logging
import logging.config

def setup_logging():
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s [%(module)s] - %(levelname)s - %(message)s',
            },
        },
        'handlers': {
            'file': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': 'application.log',
                'formatter': 'standard',
            },
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
            },
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['file', 'console'],
                'level': 'INFO',
                'propagate': True
            },
            '__main__': {
                'handlers': ['file', 'console'],
                'level': 'INFO',
                'propagate': False
            },
        }
    }

    logging.config.dictConfig(logging_config)

# Call this function to configure logging centrally
setup_logging()

# Create a logger for the module
logger = logging.getLogger(__name__)
