import logging

from bfgg.config import config


def setup_logger(name: str = "bfgg"):
    log = logging.getLogger(name=name)
    log.setLevel(config.log_level)
    formatter = logging.Formatter(
        fmt="%(asctime)s|%(levelname)s|%(module)s.%(funcName)s#%(lineno)d|%(threadName)s|%(message)s",
        datefmt="%m/%d/%Y %I:%M:%S",
    )
    ch = logging.StreamHandler()
    ch.setLevel(config.log_level)
    ch.setFormatter(formatter)
    log.addHandler(ch)
