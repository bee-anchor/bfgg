import threading
import zmq


class TaskPuller(threading.Thread):

    def __init__(self, context: zmq.Context, controller_host: str, port: str):
        threading.Thread.__init__(self)
        self.context = context
        self.controller_host = controller_host
        self.port = port

    def run(self):
        puller = self.context.socket(zmq.PULL)
        puller.connect(f"tcp://{self.controller_host}:{self.port}")
        print("TaskPuller thread started")
        while True:
            [type, identity, message] = puller.recv_multipart()
            print(type, identity, message)
