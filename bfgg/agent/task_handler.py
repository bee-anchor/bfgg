import threading
import zmq
import logging.config
from bfgg.utils.messages import CLONE, START_TEST, STOP_TEST
from bfgg.agent.state import State
from bfgg.agent.run_test import RunTest
from bfgg.agent.git_actions import clone_repo


class TaskHandler(threading.Thread):

    def __init__(self, lock: threading.Lock, state: State, context: zmq.Context, controller_host: str, port: str,
                 tests_location: str, results_folder: str, gatling_location: str):
        threading.Thread.__init__(self)
        self.lock = lock
        self.state = state
        self.context = context
        self.controller_host = controller_host
        self.port = port
        self.tests_location = tests_location
        self.results_folder = results_folder
        self.gatling_location = gatling_location
        self.test_runner = None

    def run(self):
        handler = self.context.socket(zmq.PULL)
        handler.connect(f"tcp://{self.controller_host}:{self.port}")
        logging.info("TaskHandler thread started")
        while True:
            try:
                [type, identity, message] = handler.recv_multipart()
                if type == CLONE:
                    clone_repo(message.decode("utf-8"), self.tests_location, self.lock, self.state)
                elif type == START_TEST:
                    project, test, java_opts = message.decode('utf-8').split(",")
                    self.test_runner = RunTest(self.lock, self.state, self.gatling_location, self.tests_location,
                            self.results_folder, project, test, java_opts)
                    self.test_runner.start()
                elif type == STOP_TEST:
                    self.test_runner.stop_test()
                else:
                    print(type, identity, message)
            except Exception as e:
                logging.error(e)
                continue
