import threading
import zmq
import logging.config
from bfgg.controller.state import State
from bfgg.utils.messages import STATUS, BYE


class AgentPoller(threading.Thread):
    def __init__(self, lock: threading.Lock, context: zmq.Context, port, state: State):
        threading.Thread.__init__(self)
        self.lock = lock
        self.context = context
        self.port = port
        self.state: State = state

    def run(self):
        poller = self.context.socket(zmq.PULL)
        poller.bind(f"tcp://*:{self.port}")
        logging.info("AgentPoller thread started")
        while True:
            [type, identity, message] = poller.recv_multipart()
            if type == STATUS:
                with self.lock:
                    self.state.update_agent(identity, message.decode('utf-8'))
            elif type == BYE:
                with self.lock:
                    self.state.remove_agent(identity)



