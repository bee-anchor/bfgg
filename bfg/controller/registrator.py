import threading
import zmq
from bfg.utils.messages import REGISTRATION


class Registrator(threading.Thread):

    def __init__(self, context, port, agents):
        threading.Thread.__init__(self)
        self.context = context
        self.port = port
        self.agents = agents

    def run(self):
        registrator = self.context.socket(zmq.REP)
        registrator.bind(f"tcp://*:{self.port}")
        print("Registrator thread started")
        while True:
            [type, identity, message] = registrator.recv_multipart()
            print(type, identity, message)
            self.agents.add_agent(identity)
            registrator.send_multipart([REGISTRATION, b"Master", b"Hello"])
