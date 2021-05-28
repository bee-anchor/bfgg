import os
import socket
from queue import Queue

from bfgg.agent.state import StateData
from bfgg.config import Config
from bfgg.utils.agentstatus import AgentStatus
from bfgg.utils.logging import logger
from bfgg.utils.messages import FINISHED_TEST, START_TEST, OutgoingMessage


def get_identity(controller_host):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((controller_host, 80))
    except Exception as e:
        logger.critical("Failed to get agent ip")
        logger.critical(e)
        return None
    ip = s.getsockname()[0]
    s.close()
    return ip


class AgentUtils:
    def __init__(self, state_queue: Queue, outgoing_queue: Queue, config: Config):
        self.state_queue = state_queue
        self.outgoing_queue = outgoing_queue
        self.config = config

    def handle_state_change(
        self,
        status: AgentStatus = None,
        cloned_repo: set = None,
        test_running: str = None,
        test_id: str = None,
        extra_info: str = None,
        group: str = None,
    ):
        state_changes = StateData(
            status, cloned_repo, test_running, test_id, extra_info, group
        )
        self.state_queue.put(state_changes)
        # allow the controller to know these specific state changes for handling report generation
        if status == AgentStatus.TEST_RUNNING:
            self.outgoing_queue.put(
                OutgoingMessage(START_TEST, test_id.encode("utf-8"))
            )
        elif status == AgentStatus.TEST_FINISHED:
            self.outgoing_queue.put(
                OutgoingMessage(FINISHED_TEST, test_id.encode("utf-8"))
            )

    def ensure_results_folder(self):
        if not os.path.exists(self.config.results_folder):
            os.mkdir(self.config.results_folder)
