import logging
from dotenv import load_dotenv
import os

load_dotenv()


def new_logger():
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    log.propagate = False
    formatter = logging.Formatter(fmt='%(asctime)s|%(levelname)s|%(module)s.%(funcName)s#%(lineno)d|%(threadName)s|%(message)s',
                                  datefmt='%m/%d/%Y %I:%M:%S')
    if not len(log.handlers):
        ch = logging.StreamHandler()
        ch.setLevel(os.getenv('LOG_LEVEL'))
        ch.setFormatter(formatter)
        log.addHandler(ch)
    return log


logger = new_logger()
