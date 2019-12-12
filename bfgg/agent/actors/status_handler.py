import threading
import logging.config
from queue import Empty
import pickle
from bfgg.agent.model import OUTGOING_QUEUE
from bfgg.utils.agentstatus import AgentStatus
from bfgg.agent.state_utils import AgentState, STATE_QUEUE
from bfgg.utils.messages import OutgoingMessage, STATUS


class StatusHandler(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.state: AgentState = AgentState(AgentStatus.AVAILABLE, set(), "", "")

    def run(self):
        logging.info("StatusHandler thread started")
        while True:
            self._handle_state_change()

    def _handle_state_change(self):
        try:
            state_changes: AgentState = STATE_QUEUE.get(timeout=2)
            self.state = self.state.update(state_changes)
        except Empty:
            pass
        OUTGOING_QUEUE.put(OutgoingMessage(STATUS, pickle.dumps(self.state)))
