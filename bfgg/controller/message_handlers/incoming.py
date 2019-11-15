import os
import threading
import zmq
import logging.config
from bfgg.utils.messages import LOG, STATUS, BYE
from bfgg.utils.helpers import ip_to_log_filename
from bfgg.controller.model import STATE
import pickle


class IncomingMessageHandler(threading.Thread):

    def __init__(self, context: zmq.Context, port: str, results_folder: str):
        threading.Thread.__init__(self)
        self.context = context
        self.port = port
        self.results_folder = results_folder

    def run(self):
        receiver = self.context.socket(zmq.PULL)
        receiver.bind(f"tcp://*:{self.port}")
        logging.info('IncomingMessageHandler thread started')
        while True:
            [identity, mess_type, payload] = receiver.recv_multipart()
            if mess_type == LOG:
                logging.info("Received log message")
                with open(os.path.join(self.results_folder, ip_to_log_filename(identity.decode('utf-8'))), 'a') as f:
                    f.write(payload.decode('utf-8'))
            if mess_type == STATUS:
                STATE.update_agent(identity, pickle.loads(payload))
            elif mess_type == BYE:
                STATE.remove_agent(identity)

