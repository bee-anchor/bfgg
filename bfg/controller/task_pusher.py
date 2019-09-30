import threading
import zmq
import time
from bfg.utils.messages import START_TEST, CLONE
from bfg.controller.agents import Agents


class TaskPusher(threading.Thread):

    def __init__(self, lock: threading.Lock, context: zmq.Context, port, agents: Agents):
        threading.Thread.__init__(self)
        self.lock = lock
        self.context = context
        self.port = port
        self.agents = agents

    def run(self):
        pusher = self.context.socket(zmq.PUSH)
        pusher.bind(f"tcp://*:{self.port}")
        print("TaskPusher thread started")
        while True:
            try:
                self.lock.acquire()
                current_agents = self.agents.agents.items()
                self.lock.release()
                for agent, status in current_agents:
                    print(f"{agent}: {status}")
                for agent, status in current_agents:
                    # TODO: add target to message and filtering on the agent side?
                    pusher.send_multipart([CLONE, b"Master", b"super6-perf-new"])
                time.sleep(10)
            except Exception as e:
                print(e)
                time.sleep(10)
                continue
