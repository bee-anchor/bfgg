import os
import threading
import zmq
import logging.config
from bfgg.controller.model import State
from bfgg.utils.messages import LOG, STATUS, BYE, START_TEST, FINISHED_TEST
from bfgg.utils.helpers import ip_to_log_filename, create_or_empty_folder
from bfgg.controller.actors.report_handler import ReportHandler


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

    def run(self):
        receiver = self.context.socket(zmq.PULL)
        receiver.bind(f"tcp://*:{self.port}")
        logging.info('IncomingMessageHandler thread started')
        while True:
            [identity, mess_type, payload] = receiver.recv_multipart()
            if mess_type == LOG:
                logging.info("Received log message")
                with open(os.path.join(self.results_folder, ip_to_log_filename(identity.decode('utf-8'))), 'a') as f:
                    f.write(payload.decode('utf-8'))
            elif mess_type == STATUS:
                self.state.update_agent(identity, payload)
            elif mess_type == BYE:
                self.state.remove_agent(identity)
            elif mess_type == START_TEST:
                logging.info(f"{identity.decode('utf-8')} started test")
                create_or_empty_folder(self.results_folder)
            elif mess_type == FINISHED_TEST:
                logging.info(f"{identity.decode('utf-8')} finished test")
                self.state.update_agent(identity, )
                if self.state.all_agents_finished():
                    url = ReportHandler(self.results_folder, self.gatling_location, self.s3_bucket,
                                        self.s3_region).run()
                    logging.info(url)
                else:
                    continue
