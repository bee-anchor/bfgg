from queue import Queue
from pytest import fixture
from bfgg.utils.agentstatus import AgentStatus
from bfgg.agent.utils import AgentUtils, get_identity
from bfgg.agent.state import StateData
from bfgg.utils.messages import OutgoingMessage, FINISHED_TEST


def test_get_identity(mocker):
    socket_mock = mocker.patch(
        "socket.socket",
        **{"return_value.getsockname.return_value": ["99.99.99.99", "88.88.88.88"]}
    )
    identity = "identity"
    result = get_identity(identity)
    socket_mock.return_value.connect.assert_called_with((identity, 80))
    socket_mock.return_value.getsockname.assert_called_once()
    assert "99.99.99.99" == result


class TestAgentUtils:
    @fixture()
    def mocks(self, mocker):
        outgoing_queue_mock = mocker.MagicMock(spec=Queue)
        state_queue_mock = mocker.MagicMock(spec=Queue)
        yield AgentUtils(
            state_queue_mock, outgoing_queue_mock, mocker.Mock()
        ), outgoing_queue_mock, state_queue_mock

    def test_handle_state_change(self, mocks):
        agent_utils, outgoing_queue_mock, state_queue_mock = mocks
        agent_utils.handle_state_change(
            status=AgentStatus.AVAILABLE, cloned_repo={"New repo"}
        )

        expected_state = StateData(
            AgentStatus.AVAILABLE, {"New repo"}, None, None, None, None
        )
        state_queue_mock.put.assert_called_with(expected_state)
        outgoing_queue_mock.put.assert_not_called()

    def test_handle_state_change_inc_outgoing(self, mocks):
        agent_utils, outgoing_queue_mock, state_queue_mock = mocks
        agent_utils.handle_state_change(
            status=AgentStatus.TEST_FINISHED,
            cloned_repo={"New repo"},
            test_running="New test",
            test_id="1234",
            extra_info="Really important stuff",
            group="group",
        )

        expected_state = StateData(
            AgentStatus.TEST_FINISHED,
            {"New repo"},
            "New test",
            "1234",
            "Really important stuff",
            "group",
        )
        state_queue_mock.put.assert_called_with(expected_state)
        outgoing_queue_mock.put.assert_called_with(
            OutgoingMessage(FINISHED_TEST, b"1234")
        )
