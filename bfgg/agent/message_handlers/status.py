import threading
import atexit
import time
import zmq
import logging.config
from queue import Empty
from bfgg.agent.model import STATUS_QUEUE
from bfgg.utils.messages import STATUS, BYE


class State:
    def __init__(self, identity: str):
        self.identity: bytes = identity.encode('utf-8')
        # one of: Available, Cloned, Test_Running, Test_Stopped, Test_Finished, Test_Error
        self.status: str = "Available"
        self.project: str = None
        self.test: str = None


class StatusHandler(threading.Thread):
    def __init__(self, context: zmq.Context, controller_host: str, port: str, identity: str):
        threading.Thread.__init__(self)
        self.state = State(identity)
        self.context = context
        self.controller_host = controller_host
        self.port = port
        self.stat_sender = self.context.socket(zmq.PUSH)
        self.stat_sender.connect(f"tcp://{self.controller_host}:{self.port}")
        atexit.register(self.exit_gracefully)

    def run(self):
        logging.info("StatusHandler thread started")
        while True:
            self._update_status()
            self.stat_sender.send_multipart([STATUS, self.state.identity, self.state.status.encode('utf-8')])
            time.sleep(2)

    def _update_status(self):
        while True:
            try:
                new_state = STATUS_QUEUE.get_nowait()
                self.state.status = new_state
            except Empty:
                break

    def exit_gracefully(self):
        self.stat_sender.send_multipart([BYE, self.state.identity, b"goodbye"])
        logging.info("Agent terminated")
