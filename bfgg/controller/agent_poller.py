import threading
import zmq
import logging
from bfgg.controller.state import State
from bfgg.utils.messages import STATUS, BYE


logger = logging.getLogger(__name__)


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
        logger.info("AgentPoller thread started")
        while True:
            [type, identity, message] = poller.recv_multipart()
            if type == STATUS:
                self.lock.acquire()
                self.state.update_agent(identity, message.decode('utf-8'))
                self.lock.release()
            elif type == BYE:
                self.lock.acquire()
                self.state.remove_agent(identity)
                self.lock.release()



