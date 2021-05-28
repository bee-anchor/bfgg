import threading
import time
from queue import Empty
from typing import Union

import zmq

from bfgg.controller.state import State
from bfgg.utils.logging import logger
from bfgg.utils.messages import OutgoingMessageGrouped, OutgoingMessageTargeted


class OutgoingMessageHandler(threading.Thread):
    def __init__(self, context: zmq.Context, port: int, state: State, outgoing_queue):
        super().__init__()
        self.logger = logger
        self.context = context
        self.port = port
        self.state = state
        self.outgoing_queue = outgoing_queue
        self.identity = b"controller"
        self.handler = self.context.socket(zmq.ROUTER)
        self.handler.setsockopt(zmq.ROUTER_MANDATORY, True)
        # if an agent disconnects and reconnects with the same identity,
        # router will handover connection to the 'new' one
        self.handler.setsockopt(zmq.ROUTER_HANDOVER, 1)
        self.handler.bind(f"tcp://*:{self.port}")

    def run(self):
        self.logger.info("OutgoingMessageHandler thread started")
        while True:
            try:
                self._message_handler_loop()
            except Exception as e:
                self.logger.error(e)
                time.sleep(1)
                continue

    def _message_handler_loop(self):
        self.state.handle_dead_agents()
        try:
            message: Union[
                OutgoingMessageGrouped, OutgoingMessageTargeted
            ] = self.outgoing_queue.get(timeout=1)
        except Empty:
            return
        if message is not None:
            self.send_message(message)

    def send_message(
        self, message: Union[OutgoingMessageGrouped, OutgoingMessageTargeted]
    ):
        if type(message) is OutgoingMessageGrouped:
            for agent in self.state.connected_agents_by_group(
                message.group.decode("utf-8")
            ):
                self.logger.debug([agent, self.identity, message.type, message.details])
                self.handler.send_multipart(
                    [agent, self.identity, message.type, message.details]
                )
        elif type(message) is OutgoingMessageTargeted:
            for agent in message.targets:
                self.logger.debug([agent, self.identity, message.type, message.details])
                self.handler.send_multipart(
                    [agent, self.identity, message.type, message.details]
                )
