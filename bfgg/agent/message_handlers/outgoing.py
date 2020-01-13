import threading
import zmq
import atexit
import logging.config
from bfgg.agent.model import OUTGOING_QUEUE, STATE
from bfgg.utils.messages import BYE
from bfgg.utils.messages import OutgoingMessage


class OutgoingMessageHandler(threading.Thread):

    def __init__(self, context: zmq.Context, controller_host: str, port: str, identity: bytes):
        threading.Thread.__init__(self)
        self.context = context
        self.controller_host = controller_host
        self.port = port
        self.identity = identity
        self.handler = self.context.socket(zmq.PUSH)
        self.handler.connect(f"tcp://{self.controller_host}:{self.port}")
        atexit.register(self.exit_gracefully)

    def run(self):
        logging.info("OutgoingMessageHandler thread started")
        while True:
            self._message_handler_loop()

    def _message_handler_loop(self):
        message: OutgoingMessage = OUTGOING_QUEUE.get()
        self.handler.send_multipart([self.identity, STATE.group.encode('utf-8'), message.type, message.details])

    def exit_gracefully(self):
        self.handler.send_multipart([self.identity, STATE.group.encode('utf-8'), BYE, b"goodbye"])
        logging.info("Agent terminated")
