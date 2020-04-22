from bfgg.controller.message_handlers.incoming import IncomingMessageHandler
from bfgg.controller.message_handlers.outgoing import OutgoingMessageHandler
from bfgg.controller.model import (STATE, CONTEXT, OUTGOING_QUEUE, INCOMING_PORT, OUTGOING_PORT, RESULTS_FOLDER,
                                   GATLING_LOCATION, S3_BUCKET, S3_REGION)
from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
from bfgg.controller.api import api


def create_app():
    main_app = Flask(__name__)
    CORS(main_app)
    main_app.register_blueprint(api.bp)
    main_app.wsgi_app = DispatcherMiddleware(main_app.wsgi_app, {
        '/metrics': make_wsgi_app()
    })
    return main_app


def create_controller(context=CONTEXT, incoming_port=INCOMING_PORT, outgoing_port=OUTGOING_PORT,
                      results_folder=RESULTS_FOLDER, state=STATE, outgoing_queue=OUTGOING_QUEUE,
                      gatling_location=GATLING_LOCATION, s3_bucket=S3_BUCKET, s3_region=S3_REGION):
    incoming_message_handler = IncomingMessageHandler(context, incoming_port, results_folder, state, gatling_location,
                                                      s3_bucket, s3_region)
    incoming_message_handler.name = "IncomingMessageHandler"
    incoming_message_handler.daemon = True
    incoming_message_handler.start()

    outgoing_message_handler = OutgoingMessageHandler(context, outgoing_port, state, outgoing_queue)
    outgoing_message_handler.name = "OutgoingMessageHandler"
    outgoing_message_handler.start()


app = create_app()
