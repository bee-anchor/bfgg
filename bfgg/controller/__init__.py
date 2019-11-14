import os
import logging.config
from dotenv import load_dotenv
from bfgg.controller.message_handlers.incoming import IncomingMessageHandler
from bfgg.controller.message_handlers.outgoing import OutgoingMessageHandler
from bfgg.controller.message_handlers.agent_status import AgentStatusHandler
from bfgg.controller.model import LOCK, STATE, CONTEXT, OUTGOING_QUEUE

from flask import Flask
from flask_cors import CORS
from bfgg.controller.api import api

load_dotenv()

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

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(api.bp)
    return app


def create_controller():
    incoming_port = os.getenv('CONTROLLER_MESSAGING_PORT')
    outgoing_port = os.getenv('AGENT_MESSAGING_PORT')
    status_port = os.getenv('STATUS_PORT')

    incoming_message_handler = IncomingMessageHandler(CONTEXT, incoming_port, STATE)
    incoming_message_handler.start()

    outgoing_message_handler = OutgoingMessageHandler(LOCK, CONTEXT, outgoing_port, STATE)
    outgoing_message_handler.start()

    agent_status_handler = AgentStatusHandler(LOCK, CONTEXT, status_port, STATE)
    agent_status_handler.start()


app = create_app()
