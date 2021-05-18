from queue import Queue
from pytest import fixture
from bfgg.agent.state_utils import handle_state_change_partial
from bfgg.utils.agentstatus import AgentStatus
from bfgg.agent.state import StateData
from bfgg.utils.messages import OutgoingMessage, FINISHED_TEST


class TestStateUtils:
    @fixture()
    def mocks(self, mocker):
        outgoing_queue_mock = mocker.MagicMock(spec=Queue)
        state_queue_mock = mocker.MagicMock(spec=Queue)
        yield handle_state_change_partial(
            state_queue_mock, outgoing_queue_mock
        ), outgoing_queue_mock, state_queue_mock

    def test_handle_state_change(self, mocks):
        handle_state_change, outgoing_queue_mock, state_queue_mock = mocks
        handle_state_change(status=AgentStatus.AVAILABLE, cloned_repo={"New repo"})

        expected_state = StateData(
            AgentStatus.AVAILABLE, {"New repo"}, None, None, None, None
        )
        state_queue_mock.put.assert_called_with(expected_state)
        outgoing_queue_mock.put.assert_not_called()

    def test_handle_state_change_inc_outgoing(self, mocks):
        handle_state_change, outgoing_queue_mock, state_queue_mock = mocks
        handle_state_change(
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
