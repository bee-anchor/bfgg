import threading
import time
import logging.config
from queue import Empty
import pickle
from bfgg.agent.model import STATE_QUEUE, OUTGOING_QUEUE
from bfgg.utils.statuses import Statuses
from bfgg.utils.messages import OutgoingMessage, STATUS


class State:
    def __init__(self):
        self.attributes: dict = {
            "status": Statuses.AVAILABLE,
            "cloned_repos": set(),
            "test_running": "None",
            "extra_info": "None"
        }


class StatusPoller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.state = State()

    def run(self):
        logging.info("StatusHandler thread started")
        while True:
            self._get_latest_status()
            OUTGOING_QUEUE.put(OutgoingMessage(STATUS, pickle.dumps(self.state.attributes)))
            time.sleep(2)

    def _get_latest_status(self):
        while True:
            try:
                for k, v in STATE_QUEUE.get_nowait().items():
                    if type(v) == set:
                        self.state.attributes[k].update(v)
                    else:
                        self.state.attributes[k] = v
            except Empty:
                break
