from __future__ import annotations
from typing import Union
from dataclasses import dataclass
from queue import Queue
from bfgg.utils.agentstatus import AgentStatus
from bfgg.agent.model import OUTGOING_QUEUE
from bfgg.utils.messages import OutgoingMessage, START_TEST, FINISHED_TEST

STATE_QUEUE = Queue()


@dataclass(frozen=True)
class AgentState:
    status: AgentStatus
    cloned_repos: Union[set, None]
    test_running: Union[str, None]
    extra_info: Union[str, None]

    def to_dict(self) -> dict:
        return {
            "status": self.status.name,
            "cloned_repos": list(self.cloned_repos),
            "test_running": self.test_running,
            "extra_info": self.extra_info
        }

    def update(self, changes: AgentState) -> AgentState:
        return AgentState(
            status=changes.status if changes.status is not None else self.status,
            cloned_repos=(self.cloned_repos.union(changes.cloned_repos)
                          if changes.cloned_repos is not None else self.cloned_repos),
            test_running=changes.test_running if changes.test_running is not None else self.test_running,
            extra_info=changes.extra_info if changes.extra_info is not None else self.extra_info
        )


def handle_state_change(status: AgentStatus = None, cloned_repo: set = None,
                        test_running: str = None, extra_info: str = None):
    state_changes = AgentState(status, cloned_repo, test_running, extra_info)
    STATE_QUEUE.put(state_changes)
    # allow the controller ot know these specific state changes for handling report generation
    if status == AgentStatus.TEST_RUNNING:
        OUTGOING_QUEUE.put(OutgoingMessage(START_TEST, b"started test"))
    elif status == AgentStatus.TEST_FINISHED:
        OUTGOING_QUEUE.put(OutgoingMessage(FINISHED_TEST, b"test finished"))
