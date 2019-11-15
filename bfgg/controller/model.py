import threading
import zmq
import os
from queue import Queue
import logging.config
from typing import Dict
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv

@dataclass
class Agent:
    status: str
    last_heard_from: int


class State:

    def __init__(self, lock: threading.Lock):
        self.lock = lock
        self._connected_agents: Dict[bytes, Agent] = {}

    @property
    def connected_agents(self):
        with self.lock:
            return list(self._connected_agents.keys())

    def remove_agent(self, agent):
        with self.lock:
            if agent in self._connected_agents:
                self._connected_agents.pop(agent)
                logging.info(f"{agent} disconnected")

    def update_agent(self, agent, state):
        with self.lock:
            if agent not in self._connected_agents:
                self._connected_agents[agent] = Agent(state, int(datetime.now().timestamp()))
                logging.info(f"{agent} connected, state: {state}")
            else:
                self._connected_agents[agent] = Agent(state, int(datetime.now().timestamp()))

    def current_agents_status(self):
        with self.lock:
            return {a.decode('utf-8'): s.status for a, s in self._connected_agents.items()}

    def handle_dead_agents(self):
        current_time = int(datetime.now().timestamp())
        with self.lock:
            for agent, info in self._connected_agents.items():
                # not heard from agent for over 20 seconds, something is wrong....
                if current_time - info.last_heard_from > 20:
                    self._connected_agents.pop(agent)
                    logging.warning(f"Agent {agent.decode('utf-8')} has not been heard from for a while, removing from connected list")

load_dotenv()
LOCK = threading.Lock()
STATE = State(LOCK)
CONTEXT = zmq.Context()
OUTGOING_QUEUE = Queue()
INCOMING_PORT = os.getenv('CONTROLLER_MESSAGING_PORT')
OUTGOING_PORT = os.getenv('AGENT_MESSAGING_PORT')
RESULTS_FOLDER = os.getenv('RESULTS_FOLDER')
