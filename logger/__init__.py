import logging
import sys


def get_new_logger(name=None):
    logger = logging.getLogger() if name is None else logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    return logger
