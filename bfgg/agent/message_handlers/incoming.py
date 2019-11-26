import threading
import zmq
import logging.config
from bfgg.utils.messages import CLONE, START_TEST, STOP_TEST
from bfgg.agent.actors.gatling_runner import TestRunner
from bfgg.agent.actors.git_actions import clone_repo


class IncomingMessageHandler(threading.Thread):

    def __init__(self, context: zmq.Context, controller_host: str, port: str,
                 tests_location: str, results_folder: str, gatling_location: str):
        threading.Thread.__init__(self)
        self.context = context
        self.controller_host = controller_host
        self.port = port
        self.tests_location = tests_location
        self.results_folder = results_folder
        self.gatling_location = gatling_location
        self.test_runner = None
        self.handler = self.context.socket(zmq.PULL)
        self.handler.connect(f"tcp://{self.controller_host}:{self.port}")

    def run(self):
        logging.info("IncomingMessageHandler thread started")
        while True:
            try:
                self._message_handler_loop()
            except Exception as e:
                logging.error(e)
                continue

    def _message_handler_loop(self):
        [identity, type, message] = self.handler.recv_multipart()
        if type == CLONE:
            clone_repo(message.decode("utf-8"), self.tests_location)
        elif type == START_TEST:
            project, test, java_opts = message.decode('utf-8').split(",")
            self.test_runner = TestRunner(
                self.gatling_location, self.tests_location, self.results_folder, project, test, java_opts
            )
            self.test_runner.start()
        elif type == STOP_TEST and self.test_runner is not None:
            self.test_runner.stop_runner = True
        else:
            logging.warning(f'Received unhandled message, it has been dropped: {identity}, {type}, {message}')