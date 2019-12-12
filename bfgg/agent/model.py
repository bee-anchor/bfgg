import socket
import os
import logging.config
from queue import Queue
from dotenv import load_dotenv


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


def ensure_results_folder():
    if not os.path.exists(RESULTS_FOLDER):
        os.mkdir(RESULTS_FOLDER)


OUTGOING_QUEUE = Queue()

ensure_results_folder()
IDENTITY = get_identity(CONTROLLER_HOST)
