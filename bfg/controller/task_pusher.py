import threading
import zmq
import time
from bfg.utils.messages import START_TEST
from bfg.controller.agents import Agents


class TaskPusher(threading.Thread):

    def __init__(self, context, port, agents: Agents):
        threading.Thread.__init__(self)
        self.context = context
        self.port = port
        self.agents = agents

    def run(self):
        pusher = self.context.socket(zmq.PUSH)
        pusher.bind(f"tcp://*:{self.port}")
        print("TaskPusher thread started")
        while True:
            for agent in self.agents.all_agents:
                print(f"Sending task to {agent}")
                pusher.send_multipart([START_TEST, b"Master", b"Here's some work for you"])
            time.sleep(10)
