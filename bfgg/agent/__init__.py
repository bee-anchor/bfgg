import logging.config
import zmq
import os
from bfgg.agent.message_handlers.incoming import IncomingMessageHandler
from bfgg.agent.message_handlers.outgoing import OutgoingMessageHandler
from bfgg.agent.actors.status_handler import StatusHandler
from bfgg.agent.model import (IDENTITY, CONTROLLER_HOST, AGENT_MESSAGING_PORT, CONTROLLER_MESSAGING_PORT,
                              TESTS_LOCATION, RESULTS_FOLDER, GATLING_LOCATION)

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


def create_agent(identity=IDENTITY, controller_host=CONTROLLER_HOST, agent_messaging_port=AGENT_MESSAGING_PORT,
                 controller_messaging_port=CONTROLLER_MESSAGING_PORT, tests_location=TESTS_LOCATION,
                 results_folder=RESULTS_FOLDER, gatling_location=GATLING_LOCATION):
    # Incoming Message Handler
    # Outgoing Message Handler
    # Status Message Sender

    if identity is None:
        return

    context = zmq.Context()
    # Can't be daemon, to keep process alive, and to allow it to spawn children
    incoming_message_handler = IncomingMessageHandler(context, controller_host, agent_messaging_port,
                                                      tests_location, results_folder, gatling_location)
    incoming_message_handler.start()

    outgoing_message_handler = OutgoingMessageHandler(context, controller_host, controller_messaging_port,
                                                      identity.encode('utf-8'))
    outgoing_message_handler.daemon = True
    outgoing_message_handler.start()

    status_poller = StatusHandler()
    status_poller.daemon = True
    status_poller.start()
