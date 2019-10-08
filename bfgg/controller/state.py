import logging
from typing import Union, Dict
from dataclasses import dataclass
from collections import deque
from datetime import datetime


logger = logging.getLogger(__name__)


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
        self._dead_agents: Dict[bytes, Agent] = {}
        self._task_list = deque()

    @property
    def connected_agents(self):
        return self._connected_agents.keys()

    def add_agent(self, agent):
        if agent not in self._connected_agents:
            self._connected_agents[agent] = Agent('Registered', int(datetime.now().timestamp()))

    def remove_agent(self, agent):
        if agent in self._connected_agents:
            self._connected_agents.pop(agent)
            logger.info(f"{agent} disconnected")

    def update_agent(self, agent, state):
        if agent not in self._connected_agents:
            logger.error(f"agent {agent} has not registered")
        else:
            self._connected_agents[agent] = Agent(state, int(datetime.now().timestamp()))

    def current_agents_status(self):
        state = {
            "connected": {},
            "dead": []
        }
        for agent, info in self._connected_agents.items():
            state["connected"][agent.decode('utf-8')] = info.status
        for agent, info in self._dead_agents.items():
            state["dead"].append(agent.decode('utf-8'))
        return state

    def handle_dead_agents(self):
        current_time = int(datetime.now().timestamp())
        for agent, info in self._connected_agents.items():
            # not heard from agent for over 20 seconds, something is wrong....
            if current_time - info.last_heard_from > 20:
                dead_agent_info = self._connected_agents.pop(agent)
                self._dead_agents[agent] = dead_agent_info
                logger.warning(f"Agent {agent.decode('utf-8')} has not been heard from, moving to dead agent list")

    def add_task(self, task: Task):
        self._task_list.append(task)

    def pop_next_task(self) -> Union[Task, None]:
        try:
            return self._task_list.popleft()
        except IndexError:
            return None
