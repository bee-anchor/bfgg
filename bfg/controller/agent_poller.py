import threading
import zmq
from bfg.controller.agents import Agents


class AgentPoller(threading.Thread):
    def __init__(self, lock: threading.Lock, context: zmq.Context, port, agents: Agents):
        threading.Thread.__init__(self)
        self.lock = lock
        self.context = context
        self.port = port
        self.agents = agents

    def run(self):
        poller = self.context.socket(zmq.PULL)
        poller.bind(f"tcp://*:{self.port}")
        print("AgentPoller thread started")
        while True:
            [type, identity, message] = poller.recv_multipart()
            self.lock.acquire()
            self.agents.update_agent_state(identity, message.decode('utf-8'))
            self.lock.release()


