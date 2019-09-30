import zmq
import threading
import logging
from bfg.args import bfg_args
from bfg.agent.registration import register
from bfg.agent.task_puller import TaskHandler
from bfg.agent.status_sender import StatusSender
from bfg.agent.state import State


def main():
    args = bfg_args().parse_args()
    controller_host = args.controller_host
    registrator_port = args.registrator_port
    taskpusher_port = args.task_port
    poller_port = args.poller_port

    logger = logging.Logger(__name__)
    context = zmq.Context()
    state = State()

    lock = threading.Lock()
    register(lock, state, context, controller_host, registrator_port)

    task_pusher = TaskHandler(lock, state, context, controller_host, taskpusher_port)
    task_pusher.start()

    status_sender = StatusSender(lock, state, context, controller_host, poller_port)
    status_sender.start()


if __name__ == "__main__":
    main()
