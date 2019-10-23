import logging.config
import socket
import zmq
import threading
import os
from bfgg.agent.task_handler import TaskHandler
from bfgg.agent.status_sender import StatusSender
from bfgg.agent.results_sender import ResultsSender
from bfgg.agent.state import State
from dotenv import load_dotenv

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        '': {
            'level': os.getenv('LOG_LEVEL'),
        }
    }
}

logging.config.dictConfig(DEFAULT_LOGGING)


def get_identity(controller_host):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((controller_host, 80))
    except Exception as e:
        logging.critical("Failed to get agent ip")
        logging.critical(e)
        return None
    ip = (s.getsockname()[0])
    s.close()
    return ip


def create_agent():
    load_dotenv()
    controller_host = os.getenv('CONTROLLER_HOST')
    taskpusher_port = os.getenv('TASK_PORT')
    poller_port = os.getenv('POLLER_PORT')
    results_port = os.getenv('RESULTS_PORT')
    tests_location = os.getenv('TESTS_LOCATION')
    results_folder = os.getenv('RESULTS_FOLDER')
    gatling_location = os.getenv('GATLING_LOCATION')

    identity = get_identity(controller_host)
    if identity is None:
        return

    context = zmq.Context()
    state = State(identity)
    lock = threading.Lock()

    status_sender = StatusSender(lock, state, context, controller_host, poller_port)
    status_sender.start()

    task_handler = TaskHandler(lock, state, context, controller_host, taskpusher_port,
                               tests_location, results_folder, gatling_location)
    task_handler.start()

    results_sender = ResultsSender(lock, context, results_port, state, results_folder)
    results_sender.start()
