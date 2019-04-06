import logging
import sys
import time
from functools import wraps

from awsflow.config import LOG_LEVEL


def log_duration(f):
    """
    Log duration opf `f` exection
    :param f: function to be executed
    :return:
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = f(*args, **kwargs)
        end = time.perf_counter()
        duration = end - start
        logging.info('Execution of {} took {} seconds'.format(f.__name__, duration))
        return result

    return wrapper


class logger:
    """
    logger factory
    """

    setup_done = False

    @classmethod
    def setup(cls):
        """
        Setup logger handler
        :return: logger handler
        """
        if not cls.setup_done:
            logging.root.handlers.clear()  # drop any previous default configuration
            logging.basicConfig(
                format='%(asctime)s | %(levelname)-8s | %(message)s',
                level=LOG_LEVEL
            )
            cls.setup_done = True
        return logging


def fatal(msg):
    """
    Prints message and terminates execution
    :param msg: message
    :return:
    """
    print("\nFatal error: {}; exiting.\n".format(msg))
    sys.exit(1)
