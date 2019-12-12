import threading
import zmq
import os
from queue import Queue
import logging.config
from typing import Dict
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv
from bfgg.utils.agentstatus import AgentStatus
from bfgg.agent.state_utils import AgentState


@dataclass
class Agent:
    state: AgentState
    last_heard_from: int

    def update(self, new_state: AgentState):
        self.state = new_state
        self.last_heard_from = int(datetime.now().timestamp())
        logging.debug(f"Updated agent state to {self.state} {self.last_heard_from}")


class State:

    def __init__(self, lock: threading.Lock):
        self.lock = lock
        self._connected_agents: Dict[bytes, Agent] = {}

    @property
    def connected_agents(self):
        with self.lock:
            return list(self._connected_agents.keys())

    def remove_agent(self, agent: bytes):
        with self.lock:
            if agent in self._connected_agents:
                self._connected_agents.pop(agent)
                logging.info(f"{agent} disconnected")

    def update_agent(self, agent: bytes, state: AgentState):
        with self.lock:
            if agent not in self._connected_agents:
                self._connected_agents[agent] = Agent(state, int(datetime.now().timestamp()))
                logging.info(f"{agent} connected, state: {state}")
            else:
                self._connected_agents[agent].update(state)

    def current_agents_state(self) -> Dict[str, AgentState]:
        with self.lock:
            return {a.decode('utf-8'): s.state for a, s in self._connected_agents.items()}

    def current_agents_state_dict(self) -> Dict[str, dict]:
        with self.lock:
            return {a.decode('utf-8'): s.state.to_dict() for a, s in self._connected_agents.items()}

    def all_agents_finished(self):
        agents = self.current_agents_state()
        statuses = set([i.status for i in agents.values()])
        if len(statuses) == 1 and AgentStatus.TEST_FINISHED in statuses:
            return True
        return False

    def handle_dead_agents(self):
        current_time = int(datetime.now().timestamp())
        with self.lock:
            for agent, info in self._connected_agents.items():
                # not heard from agent for over 20 seconds, something is wrong....
                if current_time - info.last_heard_from > 20:
                    self._connected_agents.pop(agent)
                    logging.warning(f"Agent {agent.decode('utf-8')} has not been heard "
                                    f"from for a while, removing from connected list")


load_dotenv()
LOCK = threading.Lock()
STATE = State(LOCK)
CONTEXT = zmq.Context()
OUTGOING_QUEUE = Queue()
INCOMING_PORT = os.getenv('CONTROLLER_MESSAGING_PORT')
OUTGOING_PORT = os.getenv('AGENT_MESSAGING_PORT')
RESULTS_FOLDER = os.getenv('RESULTS_FOLDER')
GATLING_LOCATION = os.getenv('GATLING_LOCATION')
S3_BUCKET = os.getenv('S3_BUCKET')
S3_REGION = os.getenv('S3_REGION')
