import threading
import zmq
import time
import logging.config
from queue import Empty
from bfgg.utils.messages import OutgoingMessage
from bfgg.controller.model import State


class OutgoingMessageHandler(threading.Thread):

    def __init__(self, context: zmq.Context, port: str, state: State, outgoing_queue):
        threading.Thread.__init__(self)
        self.context = context
        self.port = port
        self.state = state
        self.outgoing_queue = outgoing_queue
        self.identity = b'controller'
        self.handler = self.context.socket(zmq.ROUTER)
        self.handler.setsockopt(zmq.ROUTER_MANDATORY, True)
        # if an agent disconnects and reconnects with the same identity,
        # router will handover connection to the 'new' one
        self.handler.setsockopt(zmq.ROUTER_HANDOVER, 1)
        self.handler.bind(f"tcp://*:{self.port}")

    def run(self):
        logging.info("OutgoingMessageHandler thread started")
        while True:
            try:
                self._message_handler_loop()
            except Exception as e:
                logging.error(e)
                time.sleep(1)
                continue

    def _message_handler_loop(self):
        self.state.handle_dead_agents()
        try:
            message: OutgoingMessage = self.outgoing_queue.get(timeout=1)
        except Empty:
            return
        if message is not None:
            for agent in self.state.connected_agents:
                logging.debug([agent, self.identity, message.type, message.details])
                self.handler.send_multipart([agent, self.identity, message.type, message.details])
