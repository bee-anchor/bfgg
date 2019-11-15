import threading
import time
import logging.config
from queue import Empty
from bfgg.agent.model import STATUS_QUEUE, OUTGOING_QUEUE
from bfgg.utils.messages import STATUS, OutgoingMessage


class State:
    def __init__(self):
        self.status: str = "Available"
        # one of: Available, Cloned, Test_Running, Test_Stopped, Test_Finished, Test_Error
        self.project: str = None
        self.test: str = None


class StatusPoller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.state = State()

    def run(self):
        logging.info("StatusHandler thread started")
        while True:
            self._get_latest_status()
            OUTGOING_QUEUE.put(OutgoingMessage(STATUS, self.state.status.encode('utf-8')))
            time.sleep(2)

    def _get_latest_status(self):
        while True:
            try:
                new_state = STATUS_QUEUE.get_nowait()
                self.state.status = new_state
            except Empty:
                break
