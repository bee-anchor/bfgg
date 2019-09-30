import threading
import zmq
from bfg.utils.messages import REGISTRATION
from bfg.controller.agents import Agents


class Registrator(threading.Thread):

    def __init__(self, lock: threading.Lock, context: zmq.Context, port, agents: Agents):
        threading.Thread.__init__(self)
        self.lock = lock
        self.context = context
        self.port = port
        self.agents = agents

    def run(self):
        registrator = self.context.socket(zmq.REP)
        registrator.bind(f"tcp://*:{self.port}")
        print("Registrator thread started")
        while True:
            [type, identity, message] = registrator.recv_multipart()
            if type == REGISTRATION:
                self.lock.acquire()
                self.agents.add_agent(identity)
                self.lock.release()
            else:
                print(f"Unexpected message recieved by registrator: {type}, {identity}, {message}")
            registrator.send_multipart([REGISTRATION, b"Master", b"Hello"])
