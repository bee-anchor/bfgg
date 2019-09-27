import threading
import time
import zmq
from bfg.utils.messages import STATUS

class StatusSender(threading.Thread):
    def __init__(self, identity: bytes, context: zmq.Context, controller_host: str, port: str):
        threading.Thread.__init__(self)
        self.identity = identity
        self.context = context
        self.controller_host = controller_host
        self.port = port

    def run(self):
        stat_sender = self.context.socket(zmq.PUSH)
        stat_sender.connect(f"tcp://{self.controller_host}:{self.port}")
        print("AgentPoller thread started")
        while True:
            stat_sender.send_multipart([STATUS, self.identity, b"I'm alive"])
            time.sleep(10)
