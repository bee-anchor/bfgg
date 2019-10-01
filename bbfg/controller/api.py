from flask import Blueprint, request
from bbfg.controller.state import Task
from bbfg.utils.messages import CLONE, START_TEST, STOP_TEST, STATUS
from bbfg.controller import LOCK, STATE

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


