import threading
import time
import logging.config
from queue import Empty
from bfgg.agent.model import STATE_QUEUE, OUTGOING_QUEUE
from bfgg.utils.messages import STATUS, OutgoingMessage
from bfgg.utils.statuses import Statuses
import pickle


class State:
    def __init__(self):
        self.attributes: dict = {
            "status": Statuses.AVAILABLE.value,
            "cloned_repos": [],
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
                    if type(self.state.attributes[k]) == list:
                        if v not in self.state.attributes[k]:
                            self.state.attributes[k].append(v)
                    else:
                        self.state.attributes[k] = v
            except Empty:
                break
