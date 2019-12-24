import socket
import threading
import os
from queue import Queue
from dotenv import load_dotenv
from bfgg.agent.state import State
from bfgg.agent.state_utils import handle_state_change_partial
from bfgg.utils.logging import logger

logger = logger

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
        logger.critical("Failed to get agent ip")
        logger.critical(e)
        return None
    ip = s.getsockname()[0]
    s.close()
    return ip


def ensure_results_folder():
    if not os.path.exists(RESULTS_FOLDER):
        os.mkdir(RESULTS_FOLDER)


OUTGOING_QUEUE = Queue()
STATE_QUEUE = Queue()

IDENTITY = os.getenv('AGENT_IDENTITY', default=get_identity(CONTROLLER_HOST))
STATE = State(threading.Lock())
handle_state_change = handle_state_change_partial(STATE_QUEUE, OUTGOING_QUEUE)
