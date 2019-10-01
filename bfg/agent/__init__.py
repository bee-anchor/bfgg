import zmq
import threading
import logging
import os
from bfg.agent.registration import register
from bfg.agent.task_puller import TaskHandler
from bfg.agent.status_sender import StatusSender
from bfg.agent.state import State
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

    task_pusher = TaskHandler(lock, state, context, controller_host, taskpusher_port)
    task_pusher.start()

    status_sender = StatusSender(lock, state, context, controller_host, poller_port)
    status_sender.start()
