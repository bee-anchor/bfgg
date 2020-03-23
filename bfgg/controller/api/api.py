import os
from marshmallow import ValidationError, EXCLUDE
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from uuid import uuid4
from datetime import datetime
from bfgg.utils.messages import OutgoingMessageGrouped, CLONE, START_TEST, STOP_TEST, GROUP, OutgoingMessageTargeted
from bfgg.controller.model import STATE, DYNAMO_DB
from bfgg.controller.api.api_schemas import StartSchema, CloneSchema, GroupSchema, StopSchema, ResultsSchema
from bfgg.utils.helpers import create_or_empty_results_folder
from bfgg.controller import OUTGOING_QUEUE
from bfgg.controller.actors.report_handler import ReportHandler
from bfgg.utils.logging import logger

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
        return jsonify(err.messages), 400
    repo = result['repo']
    grp = result['group']
    OUTGOING_QUEUE.put(OutgoingMessageGrouped(CLONE, repo.encode('utf-8'), group=grp.encode('utf-8')))
    return {
        "clone": "requested"
    }


@bp.route('/start', methods=['POST'])
def start():
    try:
        result = StartSchema().load(request.get_json(force=True), unknown=EXCLUDE)
    except ValidationError as err:
        return jsonify(err.messages), bad_request
    project = result['project']
    test = result['testClass']
    java_opts = result.get('javaOpts', '')
    grp = result['group']
    test_id = str(uuid4())
    task = f"{test_id},{project},{test},{java_opts}".encode('utf-8')
    # TODO - if test already running, return error
    OUTGOING_QUEUE.put(OutgoingMessageGrouped(START_TEST, task, group=grp.encode('utf-8')))
    create_or_empty_results_folder(results_folder, grp)
    try:
        logger.info(f"Attempting to save test details: {test_id}, {project}, {test}, {java_opts}")
        DYNAMO_DB.save_test_started(test_id, datetime.utcnow(), project, test, result.get('javaOpts', None))
        logger.info("Saved details to dynamo")
    except Exception as e:
        logger.error(e)
        if hasattr(e, 'response'):
            return {"error": e.response['Error']['Message']}, 500
        else:
            return {"error": "Something went wrong"}, 500
    return {
        "test": "requested"
    }


@bp.route('/stop', methods=['POST'])
def stop():
    try:
        result = StopSchema().load(request.get_json(force=True), unknown=EXCLUDE)
    except ValidationError as err:
        return jsonify(err.messages), bad_request
    grp = result['group']
    OUTGOING_QUEUE.put(OutgoingMessageGrouped(STOP_TEST, b"STOP", group=grp.encode('utf-8')))
    return {
        "testStop": "requested"
    }


@bp.route('/status', methods=['GET'])
def status():
    current_state = STATE.current_agents_state_list()
    return jsonify(current_state)


@bp.route('/results', methods=['POST'])
def results():
    try:
        result = ResultsSchema().load(request.get_json(force=True), unknown=EXCLUDE)
    except ValidationError as err:
        return jsonify(err.messages), bad_request
    grp = result['group']
    getter = ReportHandler(results_folder, gatling_location, s3_bucket, s3_region, group=grp)
    url = getter.run()
    return {
        "Results": url
    }


@bp.route('/group', methods=['POST'])
def group():
    try:
        result = GroupSchema().load(request.get_json(force=True), unknown=EXCLUDE)
    except ValidationError as err:
        return jsonify(err.messages), 400
    new_group = result['group']
    agents = result['agents']
    OUTGOING_QUEUE.put(OutgoingMessageTargeted(GROUP, new_group.encode('utf-8'),
                                               [agent.encode('utf-8') for agent in agents]))
    return {
        "grouping": "requested"
    }


@bp.route('/past-tests', methods=['GET'])
def past_tests():
    try:
        results = DYNAMO_DB.get_all()
    except Exception as e:
        logger.error(e)
        if hasattr(e, 'response'):
            return {"error": e.response['Error']['Message']}, 500
        else:
            return {"error": "Something went wrong"}, 500
    return jsonify(results)
