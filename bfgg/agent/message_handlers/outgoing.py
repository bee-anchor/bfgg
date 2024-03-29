import threading
import zmq
import atexit
from bfgg.agent.model import OUTGOING_QUEUE, STATE
from bfgg.utils.messages import OutgoingMessage, BYE
from bfgg.utils.logging import logger


class OutgoingMessageHandler(threading.Thread):
    def __init__(
        self, context: zmq.Context, controller_host: str, port: str, identity: bytes
    ):
        super().__init__()
        self.logger = logger
        self.context = context
        self.controller_host = controller_host
        self.port = port
        self.identity = identity
        self.handler = self.context.socket(zmq.PUSH)
        self.handler.connect(f"tcp://{self.controller_host}:{self.port}")
        atexit.register(self.exit_gracefully)

    def run(self):
        self.logger.info("OutgoingMessageHandler thread started")
        while True:
            self._message_handler_loop()

    def _message_handler_loop(self):
        message: OutgoingMessage = OUTGOING_QUEUE.get()
        self.handler.send_multipart(
            [self.identity, STATE.group.encode("utf-8"), message.type, message.details]
        )

    def exit_gracefully(self):
        self.handler.send_multipart(
            [self.identity, STATE.group.encode("utf-8"), BYE, b"goodbye"]
        )
        self.logger.info("Agent terminated")
