from queue import Queue
from threading import Lock
from zmq import Context

from bfgg.controller.actors.dynamodb_resource import DynamoTableInteractor
from bfgg.controller.message_handlers.incoming import IncomingMessageHandler
from bfgg.controller.message_handlers.outgoing import OutgoingMessageHandler
from bfgg.aws import DynamoTable, S3Bucket
from bfgg.config import config, Config
from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
from bfgg.controller.api import api
from bfgg.controller.state import State

__lock = Lock()
__state = State(__lock)
__context = Context()
__outgoing_queue = Queue()
__dynamo_db = DynamoTableInteractor(config.dynamodb_table)


def create_app(
    config_: Config,
    state_: State,
    outgoing_queue: Queue,
    dynamodb: DynamoTableInteractor,
):
    main_app = Flask(__name__)
    CORS(main_app)
    main_app.register_blueprint(
        api.blueprint(config_, state_, outgoing_queue, dynamodb)
    )
    main_app.wsgi_app = DispatcherMiddleware(
        main_app.wsgi_app, {"/metrics": make_wsgi_app()}
    )
    return main_app


app = create_app(config, __state, __outgoing_queue, __dynamo_db)


def create_controller(
    context: Context = __context,
    config_: Config = config,
    state_: State = __state,
    outgoing_queue: Queue = __outgoing_queue,
):
    dynamo_interactor = DynamoTableInteractor(
        DynamoTable(
            config_.dynamodb_table, config_.aws_default_region, config_.aws_endpoint_url
        )
    )
    s3_bucket = S3Bucket(
        config_.s3_bucket, config_.s3_region, endpoint_url=config_.aws_endpoint_url
    )
    incoming_message_handler = IncomingMessageHandler(
        context,
        config_.controller_messaging_port,
        config_.results_folder,
        state_,
        config_.gatling_location,
        s3_bucket,
        dynamo_interactor,
    )
    incoming_message_handler.name = "IncomingMessageHandler"
    incoming_message_handler.daemon = True
    incoming_message_handler.start()

    outgoing_message_handler = OutgoingMessageHandler(
        context, config_.agent_messaging_port, state_, outgoing_queue
    )
    outgoing_message_handler.name = "OutgoingMessageHandler"
    outgoing_message_handler.start()
