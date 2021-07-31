import logging
import logging.config

LOG = logging.getLogger(__name__)


def config_logger(verbose: bool = False):
    console_log_level = logging.getLevelName(logging.DEBUG) if verbose else logging.getLevelName(logging.INFO)
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            }
        },
        'handlers': {
            'console': {
                'level': console_log_level,
                'formatter': 'default',
                'class': 'logging.StreamHandler'
            }
        },
        'root': {
            'handlers': ['console'],
            'level': logging.getLevelName(logging.DEBUG)
        }
    }
    logging.config.dictConfig(config=config)


def try_or(func, default=None, expected_exc=(Exception,)):
    try:
        return func()
    except expected_exc:
        return default
