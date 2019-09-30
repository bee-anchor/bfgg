import zmq
import threading
from bfg.args import bfg_args
from bfg.controller.registrator import Registrator
from bfg.controller.task_pusher import TaskPusher
from bfg.controller.agent_poller import AgentPoller
from bfg.controller.agents import Agents

def main():
    args = bfg_args().parse_args()
    registrator_port = args.registrator_port
    taskpusher_port = args.task_port
    poller_port = args.poller_port

    context = zmq.Context()
    lock = threading.Lock()
    agents = Agents()

    registrator = Registrator(lock, context, registrator_port, agents)
    registrator.start()

    task_pusher = TaskPusher(lock, context, taskpusher_port, agents)
    task_pusher.start()

    agent_poller = AgentPoller(lock, context, poller_port, agents)
    agent_poller.start()


if __name__ == "__main__":
    main()


