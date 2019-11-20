from unittest.mock import patch
import pickle
from bfgg.agent.model import get_identity, handle_state_change
from bfgg.utils.statuses import Statuses
from bfgg.utils.messages import OutgoingMessage, STATUS

@patch('socket.socket')
def test_get_identity(socket_mock):
    identity = "identity"
    socket_mock.return_value.getsockname.return_value = ['99.99.99.99', '88.88.88.88']
    result = get_identity(identity)
    socket_mock.return_value.connect.assert_called_with((identity, 80))
    socket_mock.return_value.getsockname.assert_called_once()
    assert '99.99.99.99' == result

@patch('bfgg.agent.model.OUTGOING_QUEUE')
@patch('bfgg.agent.model.STATE_QUEUE')
def test_handle_state_change(state_queue_mock, outgoing_queue_mock):
    expected = {
        "extra_info": "Really important stuff",
        "status": Statuses.TEST_FINISHED,
        "cloned_repos": {"New repo"},
        "test_running": "New test"
    }
    handle_state_change(status=Statuses.TEST_FINISHED, cloned_repo="New repo", test_running="New test",
                        extra_info="Really important stuff")

    outgoing_queue_mock.put.assert_called_with(OutgoingMessage(STATUS, pickle.dumps(expected)))
    state_queue_mock.put.assert_called_with(expected)

