from flask import Blueprint, request
from bfgg.controller.state import Task
from bfgg.utils.messages import CLONE, PREP_TEST, START_TEST, STOP_TEST, STATUS
from bfgg.controller.model import LOCK, STATE

bp = Blueprint('root', __name__)


@bp.route('/clone', methods=['POST'])
def clone():
    body = request.get_json(force=True)
    repo = body['repo']
    LOCK.acquire()
    STATE.add_task(Task(CLONE, b'MASTER', repo.encode('utf-8')))
    LOCK.release()
    return {
        "clone": "requested"
    }


@bp.route('/prep', methods=['GET'])
def prep():
    LOCK.acquire()
    STATE.add_task(Task(PREP_TEST, b'MASTER', b"get ready"))
    LOCK.release()
    return {
        "test": "prepping"
    }


@bp.route('/start', methods=['POST'])
def start():
    body = request.get_json(force=True)
    test = body['testClass']
    LOCK.acquire()
    STATE.add_task(Task(START_TEST, b'MASTER', test.encode('utf-8')))
    LOCK.release()
    return {
        "test": "requested"
    }


