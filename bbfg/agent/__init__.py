import zmq
import threading
import logging
import os
from bbfg.agent.registration import register
from bbfg.agent.task_handler import TaskHandler
from bbfg.agent.status_sender import StatusSender
from bbfg.agent.state import State
from dotenv import load_dotenv


def create_agent():
    load_dotenv()
    controller_host = os.getenv('CONTROLLER_HOST')
    registrator_port = os.getenv('REGISTRATOR_PORT')
    taskpusher_port = os.getenv('TASK_PORT')
    poller_port = os.getenv('POLLER_PORT')

    logger = logging.Logger(__name__)
    context = zmq.Context()
    state = State()

    lock = threading.Lock()
    register(lock, state, context, controller_host, registrator_port)

    status_sender = StatusSender(lock, state, context, controller_host, poller_port)
    status_sender.start()

    task_handler = TaskHandler(lock, state, context, controller_host, taskpusher_port)
    task_handler.start()
