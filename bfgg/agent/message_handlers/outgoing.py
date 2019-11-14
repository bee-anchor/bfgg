import threading
import zmq
import logging.config
from bfgg.agent.model import OUTGOING_QUEUE


class OutgoingMessageHandler(threading.Thread):

    def __init__(self, context: zmq.Context, controller_host: str, port: str,):
        threading.Thread.__init__(self)
        self.context = context
        self.controller_host = controller_host
        self.port = port

    def run(self):
        handler = self.context.socket(zmq.PULL)
        handler.connect(f"tcp://{self.controller_host}:{self.port}")
        logging.info("OutgoingMessageHandler thread started")
        while True:
            self._message_handler_loop(handler)

    @staticmethod
    def _message_handler_loop(handler):
        message = OUTGOING_QUEUE.get()
        handler.send_multipart(message)
