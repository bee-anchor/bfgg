from typing import Union
from dataclasses import dataclass
from collections import deque


@dataclass
class Task:
    type: bytes
    identity: bytes
    details: bytes


class State:

    def __init__(self):
        self._connected_agents = {}
        self._task_list = deque()

    @property
    def connected_agents(self):
        return self._connected_agents.keys()

    def add_agent(self, agent):
        if agent not in self._connected_agents:
            self._connected_agents[agent] = "Registered"

    def remove_agent(self, agent):
        if agent in self._connected_agents:
            self._connected_agents.pop(agent)
            print(f"{agent} disconnected")

    def update_agent_state(self, agent, state):
        if agent not in self._connected_agents:
            print(f"ERROR: agent {agent} has not registered")
        else:
            self._connected_agents[agent] = state

    def add_task(self, task: Task):
        self._task_list.append(task)

    def pop_next_task(self) -> Union[Task, None]:
        try:
            return self._task_list.popleft()
        except IndexError:
            return None
