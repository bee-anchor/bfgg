import threading
import time
import zmq
from bfg.utils.messages import STATUS
from bfg.agent.state import State


class StatusSender(threading.Thread):
    def __init__(self, lock: threading.Lock, state: State, context: zmq.Context, controller_host: str, port: str):
        threading.Thread.__init__(self)
        self.lock = lock
        self.state = state
        self.identity = state.identity
        self.context = context
        self.controller_host = controller_host
        self.port = port

    def run(self):
        stat_sender = self.context.socket(zmq.PUSH)
        stat_sender.connect(f"tcp://{self.controller_host}:{self.port}")
        print("AgentPoller thread started")
        while True:
            self.lock.acquire()
            stat_sender.send_multipart([STATUS, self.identity, self.state.status.encode('utf-8')])
            self.lock.release()
            time.sleep(10)
