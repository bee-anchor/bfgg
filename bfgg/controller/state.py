import logging.config
from typing import Union, Dict
from dataclasses import dataclass
from collections import deque
from datetime import datetime


@dataclass
class Task:
    type: bytes
    identity: bytes
    details: bytes

@dataclass
class Agent:
    status: str
    last_heard_from: int


class State:

    def __init__(self):
        self._connected_agents: Dict[bytes, Agent] = {}
        self._task_list = deque()

    @property
    def connected_agents(self):
        return list(self._connected_agents.keys())

    def remove_agent(self, agent):
        if agent in self._connected_agents:
            self._connected_agents.pop(agent)
            logging.info(f"{agent} disconnected")

    def update_agent(self, agent, state):
        if agent not in self._connected_agents:
            self._connected_agents[agent] = Agent(state, int(datetime.now().timestamp()))
            logging.info(f"{agent} connected, state: {state}")
        else:
            self._connected_agents[agent] = Agent(state, int(datetime.now().timestamp()))

    def current_agents_status(self):
        return {a.decode('utf-8'): s.status for a, s in self._connected_agents.items()}

    def handle_dead_agents(self):
        current_time = int(datetime.now().timestamp())
        for agent, info in self._connected_agents.items():
            # not heard from agent for over 20 seconds, something is wrong....
            if current_time - info.last_heard_from > 20:
                self._connected_agents.pop(agent)
                logging.warning(f"Agent {agent.decode('utf-8')} has not been heard from for a while, removing from connected list")

    def add_task(self, task: Task):
        self._task_list.append(task)

    def pop_next_task(self) -> Union[Task, None]:
        try:
            return self._task_list.popleft()
        except IndexError:
            return None
