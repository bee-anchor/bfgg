import threading
import os
import logging.config
from time import sleep
from pygtail import Pygtail
from bfgg.utils.messages import OutgoingMessage, LOG
from bfgg.agent.model import OUTGOING_QUEUE


class LogFollower(threading.Thread):

    def __init__(self, log_file: str):
        threading.Thread.__init__(self)
        self.log_file = log_file
        self.interval = os.getenv('LOG_SEND_INTERVAL')

    def run(self):
        logging.info("LogFollower thread started")
        log_file = Pygtail(self.log_file, full_lines=True)
        while True:
            sleep(5)
            logs = log_file.read()
            if logs:
                OUTGOING_QUEUE.put(OutgoingMessage(LOG, logs.encode('utf-8')))
                logging.info("Log queued")
