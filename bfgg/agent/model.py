import socket
import os
import logging.config
from dataclasses import dataclass
from queue import Queue
from dotenv import load_dotenv
from bfgg.utils.messages import STATUS

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

@dataclass
class OutgoingMessage:
    type: bytes
    identity: bytes
    details: bytes

OUTGOING_QUEUE = Queue()
STATUS_QUEUE = Queue()

IDENTITY = get_identity(CONTROLLER_HOST)

def handle_status_change(new_status: str):
    STATUS_QUEUE.put(new_status)
    OUTGOING_QUEUE.put(OutgoingMessage(STATUS, IDENTITY.encode('utf-8'), new_status.encode('utf8')))