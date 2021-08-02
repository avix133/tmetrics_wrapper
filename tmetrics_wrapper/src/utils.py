import logging
import logging.config

import sys

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


def add_click_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options


def query_yes_no(question, default="no"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            LOG.debug(f'Returning default answer: {default}')
            return valid[default]
        elif choice in valid:
            LOG.debug(f'User answered: {default}')
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")
