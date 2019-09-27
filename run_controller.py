import zmq
from bfg.args import bfg_args
from bfg.controller.registrator import Registrator
from bfg.controller.task_pusher import TaskPusher
from bfg.controller.agent_poller import AgentPoller
from bfg.controller.agents import Agents

args = bfg_args().parse_args()
CONTEXT = zmq.Context()

REGISTRATOR_PORT = args.registrator_port
TASKPUSHER_PORT = args.task_port
POLLER_PORT = args.poller_port


def main():
    agents = Agents()

    registrator = Registrator(CONTEXT, REGISTRATOR_PORT, agents)
    registrator.start()

    task_pusher = TaskPusher(CONTEXT, TASKPUSHER_PORT, agents)
    task_pusher.start()

    agent_poller = AgentPoller(CONTEXT, POLLER_PORT)
    agent_poller.start()


if __name__ == "__main__":
    main()


