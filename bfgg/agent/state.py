from __future__ import annotations
import threading
from typing import Optional
from dataclasses import dataclass
from bfgg.utils.agentstatus import AgentStatus


@dataclass(frozen=True)
class StateData:
    status: AgentStatus
    cloned_repos: Optional[set]
    test_running: Optional[str]
    test_id: Optional[str]
    extra_info: Optional[str]
    group: Optional[str]


class State:

    def __init__(self, lock: threading.Lock):
        self.lock = lock
        self.__state_data = StateData(AgentStatus.AVAILABLE, set(), "", "", "", "ungrouped")

    def update(self, changes: StateData):
        with self.lock:
            self.__state_data = StateData(
                status=changes.status if changes.status is not None else self.__state_data.status,
                cloned_repos=(self.__state_data.cloned_repos.union(changes.cloned_repos)
                              if changes.cloned_repos is not None else self.__state_data.cloned_repos),
                test_running=changes.test_running if changes.test_running is not None else self.__state_data.test_running,
                test_id=changes.test_id if changes.test_id is not None else self.__state_data.test_id,
                # Reset extra_info on a new state change
                extra_info=changes.extra_info if changes.extra_info is not None else "",
                group=changes.group if changes.group is not None else self.__state_data.group
            )

    @property
    def state_data(self) -> StateData:
        with self.lock:
            return self.__state_data

    @property
    def group(self) -> str:
        with self.lock:
            return self.__state_data.group
