import logging
import socket
import zmq
import threading
import os
from bfgg.agent.registration import register
from bfgg.agent.task_handler import TaskHandler
from bfgg.agent.status_sender import StatusSender
from bfgg.agent.results_sender import ResultsSender
from bfgg.agent.state import State
from dotenv import load_dotenv


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_identity(controller_host):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((controller_host, 80))
    except Exception as e:
        logger.critical("Failed to get agent ip")
        logger.critical(e)
        return None
    ip = (s.getsockname()[0])
    s.close()
    return ip


def create_agent():
    load_dotenv()
    controller_host = os.getenv('CONTROLLER_HOST')
    registrator_port = os.getenv('REGISTRATOR_PORT')
    taskpusher_port = os.getenv('TASK_PORT')
    poller_port = os.getenv('POLLER_PORT')
    results_port = os.getenv('RESULTS_PORT')
    results_folder = os.getenv('RESULTS_FOLDER')
    gatling_location = os.getenv('GATLING_LOCATION')

    identity = get_identity(controller_host)
    if identity is None:
        return

    context = zmq.Context()
    state = State(identity)

    lock = threading.Lock()
    register(lock, state, context, controller_host, registrator_port)

    status_sender = StatusSender(lock, state, context, controller_host, poller_port)
    status_sender.start()

    task_handler = TaskHandler(lock, state, context, controller_host, taskpusher_port, results_folder, gatling_location)
    task_handler.start()

    results_sender = ResultsSender(lock, context, results_port, state, results_folder)
    results_sender.start()
