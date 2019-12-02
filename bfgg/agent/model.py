import socket
import os
import logging.config
from queue import Queue
from dotenv import load_dotenv
import pickle
from bfgg.utils.messages import OutgoingMessage, STATUS
from bfgg.utils.statuses import Statuses

load_dotenv()

CONTROLLER_HOST = os.getenv('CONTROLLER_HOST')
AGENT_MESSAGING_PORT = os.getenv('AGENT_MESSAGING_PORT')
CONTROLLER_MESSAGING_PORT = os.getenv('CONTROLLER_MESSAGING_PORT')
TESTS_LOCATION = os.getenv('TESTS_LOCATION')
RESULTS_FOLDER = os.getenv('RESULTS_FOLDER')
GATLING_LOCATION = os.getenv('GATLING_LOCATION')
LOG_SEND_INTERVAL = int(os.getenv('LOG_SEND_INTERVAL'))


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


def handle_state_change(message_type: str = STATUS, status: Statuses = None, cloned_repo: str = None,
                        test_running: str = 'None', extra_info: str = 'None'):
    new_state = {
        "extra_info": extra_info
    }
    if status:
        new_state["status"] = status
    if cloned_repo:
        new_state["cloned_repos"] = {cloned_repo}
    if test_running:
        new_state["test_running"] = test_running
    OUTGOING_QUEUE.put(OutgoingMessage(message_type, pickle.dumps(new_state)))
    STATE_QUEUE.put(new_state)
