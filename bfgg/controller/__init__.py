import os
import logging
from dotenv import load_dotenv
from bfgg.controller.task_pusher import TaskPusher
from bfgg.controller.agent_poller import AgentPoller
from bfgg.controller.model import LOCK, STATE, CONTEXT

from flask import Flask
from flask_cors import CORS
from bfgg.controller import api


logging.basicConfig(level=logging.INFO)


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(api.bp)
    return app


def create_controller():
    load_dotenv()
    taskpusher_port = os.getenv('TASK_PORT')
    poller_port = os.getenv('POLLER_PORT')

    task_pusher = TaskPusher(LOCK, CONTEXT, taskpusher_port, STATE)
    task_pusher.start()

    agent_poller = AgentPoller(LOCK, CONTEXT, poller_port, STATE)
    agent_poller.start()


app = create_app()
