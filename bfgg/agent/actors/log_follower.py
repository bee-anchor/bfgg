import threading
import zmq
import os
import logging.config
from time import sleep
from pygtail import Pygtail
from bfgg.utils.messages import LOG
from bfgg.agent.model import OUTGOING_QUEUE


class LogFollower(threading.Thread):

    def __init__(self, context: zmq.Context, port: str, identity: bytes, log_file: str, controller_host: str):
        threading.Thread.__init__(self)
        self.context = context
        self.port = port
        self.controller_host = controller_host
        self.identity = identity
        self.log_file = log_file
        self.interval = os.getenv('LOG_SEND_INTERVAL')

    def data_sender_loop(self, log_file):
        sleep(5)
        logs = log_file.read()
        OUTGOING_QUEUE.put([LOG, self.identity, logs.replace('utf-8')])
        logging.debug("Log queued")

    def run(self):
        logging.info("LogSender thread started")
        log_file = Pygtail(self.log_file, full_lines=True)
        while True:
            self.data_sender_loop(log_file)



