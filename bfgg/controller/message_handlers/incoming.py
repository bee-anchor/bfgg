import os
import threading
import subprocess
import zmq
import logging.config
from bfgg.utils.messages import LOG
from bfgg.utils.helpers import ip_to_log_filename


class IncomingMessageHandler(threading.Thread):

    def __init__(self, context: zmq.Context, port, results_folder):
        threading.Thread.__init__(self)
        self.context = context
        self.port = port
        self.results_folder = results_folder

    def run(self):
        receiver = self.context.socket(zmq.PULL)
        receiver.bind(f"tcp://*:{self.port}")
        while True:
            [type, identity, logs] = receiver.recv_multipart()
            if type == LOG:
                with open(os.path.join(self.results_folder, ip_to_log_filename(identity)), 'a') as f:
                    f.write(logs.decode('utf-8'))
