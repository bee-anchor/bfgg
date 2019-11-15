import socket
import os
import logging.config
from queue import Queue
from dotenv import load_dotenv
from bfgg.utils.messages import OutgoingMessage, STATUS
from bfgg.utils.messages import STATUS, CLONED_REPO, TEST_RUNNING, EXTRA_INFO

load_dotenv()

CONTROLLER_HOST = os.getenv('CONTROLLER_HOST')
AGENT_MESSAGING_PORT = os.getenv('AGENT_MESSAGING_PORT')
CONTROLLER_MESSAGING_PORT = os.getenv('CONTROLLER_MESSAGING_PORT')
STATUS_PORT = os.getenv('STATUS_PORT')
RESULTS_PORT = os.getenv('RESULTS_PORT')
TESTS_LOCATION = os.getenv('TESTS_LOCATION')
RESULTS_FOLDER = os.getenv('RESULTS_FOLDER')
GATLING_LOCATION = os.getenv('GATLING_LOCATION')


def get_identity(controller_host):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((controller_host, 80))
    except Exception as e:
        logging.critical("Failed to get agent ip")
        logging.critical(e)
        return None
    ip = s.getsockname()[0]
    s.close()
    return ip


OUTGOING_QUEUE = Queue()
STATE_QUEUE = Queue()

IDENTITY = get_identity(CONTROLLER_HOST)


def handle_state_change(status: str = None, cloned_repo: str = None, test_running: str = None, extra_info: str = None):
    new_state = {}
    if status:
        new_state["status"] = status
     #   OUTGOING_QUEUE.put(OutgoingMessage(STATUS, IDENTITY.encode('utf-8'), status.encode('utf8')))
    if cloned_repo:
        new_state["cloned_repos"] = cloned_repo
     #   OUTGOING_QUEUE.put(OutgoingMessage(CLONED_REPO, IDENTITY.encode('utf-8'), cloned_repo.encode('utf8')))
    if test_running:
        new_state["test_running"] = test_running
     #   OUTGOING_QUEUE.put(OutgoingMessage(TEST_RUNNING, IDENTITY.encode('utf-8'), test_running.encode('utf8')))
    if extra_info:
        new_state["extra_info"] = extra_info
      #  OUTGOING_QUEUE.put(OutgoingMessage(EXTRA_INFO, IDENTITY.encode('utf-8'), extra_info.encode('utf8')))
    STATE_QUEUE.put(new_state)
