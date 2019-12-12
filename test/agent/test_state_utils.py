from pytest import fixture
from bfgg.agent.state_utils import AgentState, handle_state_change
from bfgg.utils.agentstatus import AgentStatus
from bfgg.utils.messages import OutgoingMessage, FINISHED_TEST


@fixture()
def outgoing_queue_mock(mocker):
    outgoing_queue_mock = mocker.patch('bfgg.agent.state_utils.OUTGOING_QUEUE')
    yield outgoing_queue_mock


@fixture()
def state_queue_mock(mocker):
    state_queue_mock = mocker.patch('bfgg.agent.state_utils.STATE_QUEUE')
    yield state_queue_mock


def test_agent_state_update():
    original_state = AgentState(AgentStatus.AVAILABLE, set(), "", "")
    update_state = AgentState(AgentStatus.TEST_RUNNING, {"test_repo"}, "test_1", None)
    new_state = original_state.update(update_state)
    assert new_state == AgentState(AgentStatus.TEST_RUNNING, {"test_repo"}, "test_1", "")


def test_agent_state_dict():
    state = AgentState(AgentStatus.AVAILABLE, {"test_repo"}, "test_1", "info")
    assert state.to_dict() == {
        "status": "AVAILABLE",
        "cloned_repos": ["test_repo"],
        "test_running": "test_1",
        "extra_info": "info"
    }


def test_handle_state_change(outgoing_queue_mock, state_queue_mock):
    handle_state_change(status=AgentStatus.AVAILABLE, cloned_repo={"New repo"})

    expected_state = AgentState(AgentStatus.AVAILABLE, {"New repo"}, None, None)
    state_queue_mock.put.assert_called_with(expected_state)
    outgoing_queue_mock.put.assert_not_called()


def test_handle_state_change_inc_outgoing(outgoing_queue_mock, state_queue_mock):
    handle_state_change(status=AgentStatus.TEST_FINISHED, cloned_repo={"New repo"}, test_running="New test",
                        extra_info="Really important stuff")

    expected_state = AgentState(AgentStatus.TEST_FINISHED, {"New repo"}, "New test", "Really important stuff")
    state_queue_mock.put.assert_called_with(expected_state)
    outgoing_queue_mock.put.assert_called_with(OutgoingMessage(FINISHED_TEST, b"test finished"))

