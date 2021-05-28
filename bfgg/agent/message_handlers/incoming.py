from queue import Queue
from threading import Thread
from zmq import Context, DEALER, IDENTITY
from bfgg.utils.logging import logger
from bfgg.utils.messages import CLONE, START_TEST, STOP_TEST, GROUP
from bfgg.agent.actors.gatling_runner import GatlingRunner
from bfgg.agent.actors.git_actions import clone_repo
from bfgg.agent.utils import AgentUtils


class IncomingMessageHandler(Thread):
    def __init__(
        self,
        identity: str,
        utils: AgentUtils,
        context: Context,
        controller_host: str,
        port: int,
        tests_location: str,
        results_folder: str,
        gatling_location: str,
        outgoing_queue: Queue,
        log_send_interval: float,
    ):
        super().__init__()
        self.identity = identity
        self.utils = utils
        self.logger = logger
        self.context = context
        self.controller_host = controller_host
        self.port = port
        self.tests_location = tests_location
        self.results_folder = results_folder
        self.gatling_location = gatling_location
        self.outgoing_queue = outgoing_queue
        self.log_send_interval = log_send_interval
        self.test_runner = None
        self.handler = self.context.socket(DEALER)
        self.handler.setsockopt(IDENTITY, self.identity.encode("utf-8"))
        self.handler.connect(f"tcp://{self.controller_host}:{self.port}")

    def run(self):
        self.logger.info("IncomingMessageHandler thread started")
        self.utils.ensure_results_folder()
        while True:
            try:
                self._message_handler_loop()
            except Exception as e:
                self.logger.error(e)
                continue

    def _message_handler_loop(self):
        self.logger.debug("waiting for message")
        [identity, type, message] = self.handler.recv_multipart()
        self.logger.debug([identity, type, message])
        if type == CLONE:
            clone_repo(message.decode("utf-8"), self.tests_location, self.utils)
        elif type == START_TEST:
            test_id, project, test, java_opts = message.decode("utf-8").split(",")
            self.test_runner = GatlingRunner(
                self.gatling_location,
                self.tests_location,
                self.results_folder,
                test_id,
                project,
                test,
                java_opts,
                self.outgoing_queue,
                self.log_send_interval,
                self.utils,
            )
            self.test_runner.name = f"GatlingRunner_{test}"
            self.test_runner.start()
        elif type == STOP_TEST and self.test_runner is not None:
            self.test_runner.stop_runner = True
        elif type == GROUP:
            self.utils.handle_state_change(group=message.decode("utf-8"))
        else:
            self.logger.warning(
                f"Received unhandled message, it has been dropped: {identity}, {type}, {message}"
            )
