import logging
from pathlib import Path, PurePath
import zmq
import threading
import os
from bfgg.agent.registration import register
from bfgg.agent.task_handler import TaskHandler
from bfgg.agent.status_sender import StatusSender
from bfgg.agent.state import State
from dotenv import load_dotenv


logging.basicConfig(filename=f"{str(PurePath(str(Path.home()), 'bfgg_agent.log'))}", level=logging.DEBUG)


def create_agent():
    load_dotenv()
    controller_host = os.getenv('CONTROLLER_HOST')
    registrator_port = os.getenv('REGISTRATOR_PORT')
    taskpusher_port = os.getenv('TASK_PORT')
    poller_port = os.getenv('POLLER_PORT')

    context = zmq.Context()
    state = State()

    lock = threading.Lock()
    register(lock, state, context, controller_host, registrator_port)

    status_sender = StatusSender(lock, state, context, controller_host, poller_port)
    status_sender.start()

    task_handler = TaskHandler(lock, state, context, controller_host, taskpusher_port)
    task_handler.start()
