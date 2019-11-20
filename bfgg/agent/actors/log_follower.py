import threading
import os
from datetime import datetime
import logging.config
from time import sleep
from pygtail import Pygtail
from bfgg.utils.messages import OutgoingMessage, LOG
from bfgg.agent.model import OUTGOING_QUEUE, LOG_SEND_INTERVAL


class LogFollower(threading.Thread):

    def __init__(self, results_folder: str):
        threading.Thread.__init__(self)
        self.results_folder = results_folder
        self.stop_thread = False

    def _get_current_logfile(self):
        while True:
            result_folders = os.listdir(self.results_folder)
            folders = [os.path.join(self.results_folder, x) for x in result_folders if
                       os.path.isdir(os.path.join(self.results_folder, x))]
            newest_folder = max(folders, key=os.path.getmtime)
            newest_folder_mtime = os.path.getmtime(newest_folder)
            now = datetime.now().timestamp()
            # folder should have been modified recently
            if (now - newest_folder_mtime) < 3:
                path = os.path.join(newest_folder, "simulation.log")
                return path
            else:
                sleep(1)
                continue

    def run(self):
        logging.info("LogFollower thread started")
        current_log_file = self._get_current_logfile()
        logging.info(f"Following log file: {current_log_file}")
        log_file = Pygtail(current_log_file, full_lines=True)
        while True:
            sleep(LOG_SEND_INTERVAL)
            logs = log_file.read()
            if logs:
                OUTGOING_QUEUE.put(OutgoingMessage(LOG, logs.encode('utf-8')))
                logging.debug("Log queued")
            if self.stop_thread:
                logging.debug("Stopping log follower")
                break
