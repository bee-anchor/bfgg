import logging.config
import threading
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
from bfgg.utils.agentstatus import AgentStatus
from bfgg.agent.state import StateData


@dataclass
class Agent:
    state: StateData
    last_heard_from: int

    def update(self, new_state: StateData):
        self.state = new_state
        self.last_heard_from = int(datetime.now().timestamp())
        logging.debug(f"Updated agent state to {self.state} {self.last_heard_from}")

    def to_dict(self) -> dict:
        return {
            "status": self.state.status.name,
            "cloned_repos": list(self.state.cloned_repos),
            "test_running": self.state.test_running,
            "extra_info": self.state.extra_info,
            "group": self.state.group
        }


class State:

    def __init__(self, lock: threading.Lock):
        self.lock = lock
        self._current_agents: Dict[bytes, Agent] = {}

    @property
    def connected_agents(self) -> List[bytes]:
        with self.lock:
            return list(self._current_agents.keys())

    def connected_agents_by_group(self, group: str) -> List[bytes]:
        with self.lock:
            return [a for a, s in self._current_agents.items() if s.state.group == group]

    def remove_agent(self, agent: bytes):
        with self.lock:
            if agent in self._current_agents:
                self._current_agents.pop(agent)
                logging.info(f"{agent} disconnected")

    def update_agent_state(self, agent: bytes, state: StateData):
        with self.lock:
            if agent not in self._current_agents:
                self._current_agents[agent] = Agent(state, int(datetime.now().timestamp()))
                logging.info(f"{agent} connected, state: {state}")
            else:
                self._current_agents[agent].update(state)

    def update_agent_status(self, agent: bytes, status: AgentStatus):
        with self.lock:
            if agent not in self._current_agents:
                logging.warning(f"Tried to update status to {status.name} for unknown agent {agent}")
            else:
                self._current_agents[agent].state.status = status

    def current_agents_state(self) -> Dict[bytes, StateData]:
        with self.lock:
            return {i: a.state for (i, a) in self._current_agents.items()}

    def current_agents_state_by_group(self, group: str) -> Dict[bytes, StateData]:
        with self.lock:
            return {i: a.state for (i, a) in self._current_agents.items() if a.state.group == group}

    def current_agents_state_dict(self) -> Dict[str, dict]:
        with self.lock:
            return {i.decode('utf-8'): a.to_dict() for i, a in self._current_agents.items()}

    def current_groups(self) -> List[str]:
        groups = list(set([a.state.group for i, a in self._current_agents.items()]))
        return list(filter(lambda i: i != '', groups))

    def all_agents_finished(self):
        agents = self.current_agents_state()
        statuses = set([i.status for i in agents.values()])
        if len(statuses) == 1 and AgentStatus.TEST_FINISHED in statuses:
            return True
        return False

    def all_agents_finished_in_group(self, group):
        agents = self.current_agents_state_by_group(group)
        statuses = set([i.status for i in agents.values()])
        if len(statuses) == 1 and AgentStatus.TEST_FINISHED in statuses:
            return True
        return False

    def handle_dead_agents(self):
        current_time = int(datetime.now().timestamp())
        with self.lock:
            updated_agents = self._current_agents.copy()
            for agent, info in updated_agents.items():
                # not heard from agent for over 20 seconds, something is wrong....
                if current_time - info.last_heard_from > 20:
                    self._current_agents.pop(agent)
                    logging.warning(f"Agent {agent.decode('utf-8')} has not been heard "
                                    f"from for a while, removing from connected list")
