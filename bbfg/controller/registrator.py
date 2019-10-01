import threading
import zmq
from bbfg.utils.messages import REGISTRATION
from bbfg.controller.state import State


class Registrator(threading.Thread):

    def __init__(self, lock: threading.Lock, context: zmq.Context, port, state: State):
        threading.Thread.__init__(self)
        self.lock = lock
        self.context = context
        self.port = port
        self.state = state

    def run(self):
        registrator = self.context.socket(zmq.REP)
        registrator.bind(f"tcp://*:{self.port}")
        print("Registrator thread started")
        while True:
            [type, identity, message] = registrator.recv_multipart()
            if type == REGISTRATION:
                self.lock.acquire()
                self.state.add_agent(identity)
                self.lock.release()
            else:
                print(f"Unexpected message recieved by registrator: {type}, {identity}, {message}")
            registrator.send_multipart([REGISTRATION, b"Master", b"Hello"])
