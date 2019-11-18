import threading
import zmq
import time
import logging.config
from queue import Empty
from bfgg.utils.messages import OutgoingMessage


class OutgoingMessageHandler(threading.Thread):

    def __init__(self, context: zmq.Context, port: str, state, outgoing_queue):
        threading.Thread.__init__(self)
        self.context = context
        self.port = port
        self.state = state
        self.outgoing_queue = outgoing_queue
        self.identity = b'controller'

    def run(self):
        pusher = self.context.socket(zmq.PUSH)
        pusher.bind(f"tcp://*:{self.port}")
        logging.info("OutgoingMessageHandler thread started")
        while True:
            try:
                self.state.handle_dead_agents()
                try:
                    message: OutgoingMessage = self.outgoing_queue.get(timeout=1)
                except Empty:
                    continue
                current_agents = self.state.connected_agents
                for _ in current_agents:
                    # round robins to each connected agent
                    pusher.send_multipart([self.identity, message.type, message.details])
            except Exception as e:
                logging.error(e)
                time.sleep(1)
                continue
