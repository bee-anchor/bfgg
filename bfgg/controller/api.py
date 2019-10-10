from flask import Blueprint, request
from bfgg.controller.state import Task
from bfgg.utils.messages import CLONE, PREP_TEST, START_TEST, STOP_TEST, STATUS
from bfgg.controller.model import LOCK, STATE

bp = Blueprint('root', __name__)


@bp.route('/clone', methods=['POST'])
def clone():
    body = request.get_json(force=True)
    repo = body['repo']
    with LOCK:
        STATE.add_task(Task(CLONE, b'MASTER', repo.encode('utf-8')))
    return {
        "clone": "requested"
    }


@bp.route('/prep', methods=['POST'])
def prep():
    with LOCK:
        STATE.add_task(Task(PREP_TEST, b'MASTER', b"get ready"))
    return {
        "test": "prepping"
    }


@bp.route('/start', methods=['POST'])
def start():
    body = request.get_json(force=True)
    test = body['testClass']
    with LOCK:
        STATE.add_task(Task(START_TEST, b'MASTER', test.encode('utf-8')))
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
