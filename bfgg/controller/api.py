import os
from concurrent import futures
from dotenv import load_dotenv
from flask import Blueprint, request
from bfgg.controller.state import Task
from bfgg.utils.messages import CLONE, PREP_TEST, START_TEST, STOP_TEST, STATUS
from bfgg.controller.model import LOCK, STATE, CONTEXT
from bfgg.controller.results_getter import ResultsGetter

bp = Blueprint('root', __name__)

load_dotenv()
results_port = os.getenv('RESULTS_PORT')
results_file = os.getenv('RESULTS_FOLDER')
gatling_location = os.getenv('GATLING_LOCATION')
s3_bucket = os.getenv('S3_BUCKET')
s3_region = os.getenv('S3_REGION')

@bp.route('/clone', methods=['POST'])
def clone():
    body = request.get_json(force=True)
    repo = body['repo']
    with LOCK:
        STATE.add_task(Task(CLONE, b'MASTER', repo.encode('utf-8')))
    return {
        "clone": "requested"
    }


@bp.route('/start', methods=['POST'])
def start():
    body: dict = request.get_json(force=True)
    project = body['project']
    test = body['testClass']
    javaOpts = body.get('javaOpts', '')
    task = f"{project},{test},{javaOpts}".encode('utf-8')
    with LOCK:
        STATE.add_task(Task(START_TEST, b'MASTER', task))
    return {
        "test": "requested"
    }


@bp.route('/stop', methods=['POST'])
def stop():
    with LOCK:
        STATE.add_task(Task(STOP_TEST, b'MASTER', b"STOP"))
    return {
        "testStop": "requested"
    }


@bp.route('/status', methods=['GET'])
def status():
    with LOCK:
        current_status = STATE.current_agents_status()
    return current_status


@bp.route('/results', methods=['GET'])
def results():
    getter = ResultsGetter(LOCK, CONTEXT, results_port, STATE, results_file, gatling_location, s3_bucket, s3_region)
    # executor = futures.ThreadPoolExecutor(max_workers=1)
    # executor.submit(getter.get_results)
    url = getter.get_results()
    return {
        "Results": url
    }
