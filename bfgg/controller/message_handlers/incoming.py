import threading
import zmq
import logging.config
from bfgg.controller.model import State
import pickle
from bfgg.utils.messages import LOG, STATUS, BYE, START_TEST, FINISHED_TEST
from bfgg.controller.actors.report_handler import ReportHandler
from bfgg.controller.actors.metrics_handler import MetricsHandler
from bfgg.utils.helpers import create_or_empty_results_folder
from bfgg.utils.agentstatus import AgentStatus


class IncomingMessageHandler(threading.Thread):

    def __init__(self, context: zmq.Context, port: str, results_folder: str, state: State, gatling_location: str,
                 s3_bucket: str, s3_region: str):
        threading.Thread.__init__(self)
        self.context = context
        self.port = port
        self.results_folder = results_folder
        self.state = state
        self.gatling_location = gatling_location
        self.s3_bucket = s3_bucket
        self.s3_region = s3_region
        self.metrics_handler = MetricsHandler(results_folder)
        self.handler = self.context.socket(zmq.PULL)

    def run(self):
        self.handler.bind(f"tcp://*:{self.port}")
        logging.info('IncomingMessageHandler thread started')
        while True:
            try:
                self._message_handler_loop()
            # Continue no matter what
            except Exception as e:
                logging.error(e)
                continue

    def _message_handler_loop(self):
        [identity, group, mess_type, payload] = self.handler.recv_multipart()
        if mess_type == LOG:
            self.metrics_handler.handle_log(identity, payload, group)
        elif mess_type == STATUS:
            self.state.update_agent_state(identity, pickle.loads(payload))
        elif mess_type == BYE:
            self.state.remove_agent(identity)
        elif mess_type == START_TEST:
            logging.info(f"{identity.decode('utf-8')} started test")
            create_or_empty_results_folder(self.results_folder, group)
        elif mess_type == FINISHED_TEST:
            logging.info(f"{identity.decode('utf-8')} finished test")
            self.state.update_agent_status(identity, AgentStatus.TEST_FINISHED)
            if self.state.all_agents_finished_in_group(group):
                ReportHandler(self.results_folder, self.gatling_location, self.s3_bucket,
                              self.s3_region, group).run()
