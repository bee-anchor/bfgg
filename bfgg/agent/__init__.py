from zmq import Context
from threading import Lock
from queue import Queue
from bfgg.config import config, Config
from bfgg.agent.state import State
from bfgg.agent.utils import AgentUtils, get_identity
from bfgg.agent.message_handlers.incoming import IncomingMessageHandler
from bfgg.agent.message_handlers.outgoing import OutgoingMessageHandler
from bfgg.agent.actors.status_handler import StatusHandler

__context = Context()
__state = State(Lock())
__outgoing_queue = Queue()
__state_queue = Queue()


def create_agent(
    config_: Config = config,
    state: State = __state,
    outgoing_queue: Queue = __outgoing_queue,
    state_queue: Queue = __state_queue,
    context: Context = __context,
):
    if config_.agent_identity is None:
        identity = get_identity(config_.controller_host)
    else:
        identity = config_.agent_identity
    if identity is None:
        return

    # Can't be daemon, to keep process alive, and to allow it to spawn children
    incoming_message_handler = IncomingMessageHandler(
        identity,
        AgentUtils(state_queue, outgoing_queue, config_),
        context,
        config_.controller_host,
        config_.agent_messaging_port,
        config_.tests_location,
        config_.results_folder,
        config_.gatling_location,
        outgoing_queue,
        config_.log_send_interval,
    )
    incoming_message_handler.name = "IncomingMessageHandler"
    incoming_message_handler.start()

    outgoing_message_handler = OutgoingMessageHandler(
        context,
        state,
        outgoing_queue,
        config_.controller_host,
        config_.controller_messaging_port,
        identity.encode("utf-8"),
    )
    outgoing_message_handler.name = "OutgoingMessageHandler"
    outgoing_message_handler.daemon = True
    outgoing_message_handler.start()

    status_handler = StatusHandler(state, state_queue, outgoing_queue)
    status_handler.name = "StatusHandler"
    status_handler.daemon = True
    status_handler.start()
