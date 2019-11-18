import threading
import time
import logging.config
from queue import Empty
from bfgg.agent.model import STATUS_QUEUE, OUTGOING_QUEUE
from bfgg.utils.messages import STATUS, OutgoingMessage, Statuses


class State:
    def __init__(self):
        self.status: Statuses = Statuses.AVAILABLE
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
            OUTGOING_QUEUE.put(OutgoingMessage(STATUS, self.state.status.value))
            time.sleep(2)

    def _get_latest_status(self):
        while True:
            try:
                state_value = STATUS_QUEUE.get_nowait()
                self.state.status = Statuses(state_value)
            except Empty:
                break
