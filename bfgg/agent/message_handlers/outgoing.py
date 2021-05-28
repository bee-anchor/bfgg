import atexit
import threading
from queue import Queue

from zmq import PUSH, Context

from bfgg.agent import State
from bfgg.utils.logging import logger
from bfgg.utils.messages import BYE, OutgoingMessage


class OutgoingMessageHandler(threading.Thread):
    def __init__(
        self,
        context: Context,
        state: State,
        outgoing_queue: Queue,
        controller_host: str,
        port: int,
        identity: bytes,
    ):
        super().__init__()
        self.logger = logger
        self.context = context
        self.state = state
        self.outgoing_queue = outgoing_queue
        self.controller_host = controller_host
        self.port = port
        self.identity = identity
        self.handler = self.context.socket(PUSH)
        self.handler.connect(f"tcp://{self.controller_host}:{self.port}")
        atexit.register(self.exit_gracefully)

    def run(self):
        self.logger.info("OutgoingMessageHandler thread started")
        while True:
            self._message_handler_loop()

    def _message_handler_loop(self):
        message: OutgoingMessage = self.outgoing_queue.get()
        self.handler.send_multipart(
            [
                self.identity,
                self.state.group.encode("utf-8"),
                message.type,
                message.details,
            ]
        )

    def exit_gracefully(self):
        self.handler.send_multipart(
            [self.identity, self.state.group.encode("utf-8"), BYE, b"goodbye"]
        )
        self.logger.info("Agent terminated")
