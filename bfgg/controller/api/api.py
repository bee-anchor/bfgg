import os
from marshmallow import ValidationError, EXCLUDE
from dotenv import load_dotenv
from flask import Blueprint, request
import json
from bfgg.utils.messages import OutgoingMessage, CLONE, START_TEST, STOP_TEST
from bfgg.controller.model import STATE
from bfgg.controller.api.api_schemas import StartSchema, CloneSchema
from bfgg.utils.helpers import create_or_empty_folder
from bfgg.controller import OUTGOING_QUEUE
from bfgg.controller.actors.report_handler import ReportHandler
from bfgg.utils.statuses import Statuses

bp = Blueprint('root', __name__)

load_dotenv()
results_port = os.getenv('RESULTS_PORT')
results_folder = os.getenv('RESULTS_FOLDER')
gatling_location = os.getenv('GATLING_LOCATION')
s3_bucket = os.getenv('S3_BUCKET')
s3_region = os.getenv('S3_REGION')

bad_request = 400


@bp.route('/clone', methods=['POST'])
def clone():
    try:
        result = CloneSchema().load(request.get_json(force=True), unknown=EXCLUDE)
    except ValidationError as err:
        return err.messages, bad_request
    repo = result['repo']
    OUTGOING_QUEUE.put(OutgoingMessage(CLONE, repo.encode('utf-8')))
    return {
        "clone": "requested"
    }


@bp.route('/start', methods=['POST'])
def start():
    try:
        result = StartSchema().load(request.get_json(force=True), unknown=EXCLUDE)
    except ValidationError as err:
        return err.messages, bad_request
    project = result['project']
    test = result['testClass']
    javaOpts = result.get('javaOpts', '')
    task = f"{project},{test},{javaOpts}".encode('utf-8')
    # TODO - if test already running, return error
    OUTGOING_QUEUE.put(OutgoingMessage(START_TEST, task))
    create_or_empty_folder(results_folder)
    return {
        "test": "requested"
    }


@bp.route('/stop', methods=['POST'])
def stop():
    OUTGOING_QUEUE.put(OutgoingMessage(STOP_TEST, b"STOP"))
    return {
        "testStop": "requested"
    }


@bp.route('/status', methods=['GET'])
def status():
    current_state = STATE.current_agents_state()
    return json.dumps(current_state, cls=_StatusEncoder)


@bp.route('/results', methods=['GET'])
def results():
    getter = ReportHandler(results_folder, gatling_location, s3_bucket, s3_region)
    url = getter.run()
    return {
        "Results": url
    }


class _StatusEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) == set:
            return list(obj)
        elif type(obj) == Statuses:
            return obj.name
        return super().default(obj)
