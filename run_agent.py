import zmq
import logging
import uuid
from bfg.args import bfg_args
from bfg.agent.registration import register
from bfg.agent.task_puller import TaskPuller
from bfg.agent.status_sender import StatusSender

args = bfg_args().parse_args()
IDENTITY = str(uuid.uuid1()).encode('UTF-8')

logger = logging.Logger(__name__)

CONTROLLER_HOST = args.controller_host
REGISTRATOR_PORT = args.registrator_port
TASKPUSHER_PORT = args.task_port
POLLER_PORT = args.poller_port

CONTEXT = zmq.Context()

def main():
    register(IDENTITY, CONTEXT, CONTROLLER_HOST, REGISTRATOR_PORT)

    task_pusher = TaskPuller(CONTEXT, CONTROLLER_HOST, TASKPUSHER_PORT)
    task_pusher.start()

    agent_poller = StatusSender(IDENTITY, CONTEXT, CONTROLLER_HOST, POLLER_PORT)
    agent_poller.start()


if __name__ == "__main__":
    main()
