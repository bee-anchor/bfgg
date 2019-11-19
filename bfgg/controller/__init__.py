import os
import logging.config
from bfgg.controller.message_handlers.incoming import IncomingMessageHandler
from bfgg.controller.message_handlers.outgoing import OutgoingMessageHandler
from bfgg.controller.model import (STATE, CONTEXT, OUTGOING_QUEUE, INCOMING_PORT, OUTGOING_PORT, RESULTS_FOLDER,
                                   GATLING_LOCATION, S3_BUCKET, S3_REGION)

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


def create_controller(context=CONTEXT, incoming_port=INCOMING_PORT, outgoing_port=OUTGOING_PORT,
                      results_folder=RESULTS_FOLDER, state=STATE, outgoing_queue=OUTGOING_QUEUE,
                      gatling_location=GATLING_LOCATION, s3_bucket=S3_BUCKET, s3_region=S3_REGION):

    incoming_message_handler = IncomingMessageHandler(context, incoming_port, results_folder, state, gatling_location,
                                                      s3_bucket, s3_region)
    incoming_message_handler.daemon = True
    incoming_message_handler.start()

    outgoing_message_handler = OutgoingMessageHandler(context, outgoing_port, state, outgoing_queue)
    outgoing_message_handler.start()


app = create_app()
