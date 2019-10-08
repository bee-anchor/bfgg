import threading
import zmq
import logging
from bfgg.utils.messages import REGISTRATION
from bfgg.controller.state import State


logger = logging.getLogger(__name__)


class Registrator(threading.Thread):

    def __init__(self, lock: threading.Lock, context: zmq.Context, port, state: State):
        threading.Thread.__init__(self)
        self.lock = lock
        self.context = context
        self.port = port
        self.state = state

    def run(self):
        registrator = self.context.socket(zmq.REP)
        registrator.bind(f"tcp://*:{self.port}")
        logger.info("Registrator thread started")
        while True:
            [type, identity, message] = registrator.recv_multipart()
            if type == REGISTRATION:
                with self.lock:
                    self.state.add_agent(identity)
                logger.info(f"Agent registered - {identity.decode('utf-8')}")
            else:
                logger.error(f"Unexpected message recieved by registrator - {type}, {identity}, {message}")
            registrator.send_multipart([REGISTRATION, b"Master", b"Hello"])
