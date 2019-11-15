import os
import logging.config
from bfgg.controller.message_handlers.incoming import IncomingMessageHandler
from bfgg.controller.message_handlers.outgoing import OutgoingMessageHandler
from bfgg.controller.model import LOCK, STATE, CONTEXT, OUTGOING_QUEUE, INCOMING_PORT, OUTGOING_PORT, RESULTS_FOLDER

from flask import Flask
from flask_cors import CORS
from bfgg.controller.api import api

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


def create_controller(incoming_port=INCOMING_PORT, outgoing_port=OUTGOING_PORT, results_folder=RESULTS_FOLDER):

    incoming_message_handler = IncomingMessageHandler(CONTEXT, incoming_port, results_folder)
    incoming_message_handler.start()

    outgoing_message_handler = OutgoingMessageHandler(CONTEXT, outgoing_port)
    outgoing_message_handler.start()


app = create_app()
