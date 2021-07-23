import pickle
import threading
from queue import Empty, Queue
import logging

from bfgg.agent.state import State, StateData
from bfgg.utils.messages import STATUS, OutgoingMessage


class StatusHandler(threading.Thread):
    def __init__(
        self,
        state: State,
        state_queue: Queue,
        outgoing_queue: Queue,
        logger=logging.getLogger(__name__),
    ):
        super().__init__()
        self.logger = logger
        self.state = state
        self.state_queue = state_queue
        self.outgoing_queue = outgoing_queue

    def run(self):
        self.logger.info("StatusHandler thread started")
        while True:
            self._handle_state_change()

    def _handle_state_change(self):
        try:
            state_changes: StateData = self.state_queue.get(timeout=2)
            self.state.update(state_changes)
        except Empty:
            pass
        self.outgoing_queue.put(
            OutgoingMessage(STATUS, pickle.dumps(self.state.state_data))
        )
