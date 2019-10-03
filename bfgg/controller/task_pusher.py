import threading
import zmq
import time
from bfgg.controller.state import State


class TaskPusher(threading.Thread):

    def __init__(self, lock: threading.Lock, context: zmq.Context, port, state: State):
        threading.Thread.__init__(self)
        self.lock = lock
        self.context = context
        self.port = port
        self.state = state

    def run(self):
        pusher = self.context.socket(zmq.PUSH)
        pusher.bind(f"tcp://*:{self.port}")
        print("TaskPusher thread started")
        while True:
            try:
                self.lock.acquire()
                task = self.state.pop_next_task()
                current_agents = self.state.connected_agents
                self.lock.release()
                if task:
                    for _ in current_agents:
                        # round robins to each connected agent
                        pusher.send_multipart([task.type, task.identity, task.details])
                time.sleep(1)
            except Exception as e:
                print(e)
                time.sleep(1)
                continue
