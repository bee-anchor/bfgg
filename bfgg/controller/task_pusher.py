import threading
import zmq
import time
import logging
from bfgg.controller.state import State


logger = logging.getLogger(__name__)


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
        logger.info("TaskPusher thread started")
        while True:
            try:
                with self.lock:
                    self.state.handle_dead_agents()
                    task = self.state.pop_next_task()
                    current_agents = list(self.state.connected_agents)
                if task:
                    for _ in current_agents:
                        # round robins to each connected agent
                        pusher.send_multipart([task.type, task.identity, task.details])
                time.sleep(1)
            except Exception as e:
                logger.error(e)
                time.sleep(1)
                continue
