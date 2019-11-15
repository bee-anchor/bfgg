import threading
import zmq
import time
import logging.config
from queue import Empty
from bfgg.controller.model import OUTGOING_QUEUE, STATE
from bfgg.utils.messages import OutgoingMessage


class OutgoingMessageHandler(threading.Thread):

    def __init__(self, context: zmq.Context, port: str):
        threading.Thread.__init__(self)
        self.context = context
        self.port = port
        self.identity = b'controller'

    def run(self):
        pusher = self.context.socket(zmq.PUSH)
        pusher.bind(f"tcp://*:{self.port}")
        logging.info("OutgoingMessageHandler thread started")
        while True:
            try:
                STATE.handle_dead_agents()
                try:
                    message: OutgoingMessage = OUTGOING_QUEUE.get(timeout=1)
                except Empty:
                    continue
                current_agents = STATE.connected_agents
                for _ in current_agents:
                    # round robins to each connected agent
                    pusher.send_multipart([self.identity, message.type, message.details])
            except Exception as e:
                logging.error(e)
                time.sleep(1)
                continue
