import threading
import zmq


class AgentPoller(threading.Thread):
    def __init__(self, context, port):
        threading.Thread.__init__(self)
        self.context = context
        self.port = port

    def run(self):
        poller = self.context.socket(zmq.PULL)
        poller.bind(f"tcp://*:{self.port}")
        print("AgentPoller thread started")
        while True:
            [type, identity, message] = poller.recv_multipart()
            print(type, identity, message)
