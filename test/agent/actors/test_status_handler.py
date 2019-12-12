from pytest import fixture
from queue import Empty
import pickle
from bfgg.agent.actors.status_handler import StatusHandler
from bfgg.utils.agentstatus import AgentStatus
from bfgg.agent.state_utils import AgentState
from bfgg.utils.messages import OutgoingMessage, STATUS


class TestStatusHandler:

    new_state = AgentState(
        status=AgentStatus.TEST_RUNNING,
        cloned_repos=None,
        test_running="test",
        extra_info="interesting stuff"
    )

    expected_new_state = AgentState(
        status=AgentStatus.TEST_RUNNING,
        cloned_repos=set(),
        test_running="test",
        extra_info="interesting stuff"
    )

    expected_original_state = AgentState(
        status=AgentStatus.AVAILABLE,
        cloned_repos=set(),
        test_running="",
        extra_info=""
    )

    @fixture()
    def mocks(self, mocker):
        mocker.patch('bfgg.agent.actors.status_handler.threading')
        state_queue = mocker.patch('bfgg.agent.actors.status_handler.STATE_QUEUE')
        outgoing_queue = mocker.patch('bfgg.agent.actors.status_handler.OUTGOING_QUEUE')
        yield state_queue, outgoing_queue

    def test_handle_state_change_new_state(self, mocks):
        state_queue, outgoing_queue = mocks
        state_queue.configure_mock(**{'get.return_value': self.new_state})

        status_handler = StatusHandler()
        status_handler._handle_state_change()
        assert self.expected_new_state == status_handler.state
        outgoing_queue.put.assert_called_with(
            OutgoingMessage(STATUS, pickle.dumps(self.expected_new_state))
        )

    def test_handle_state_change_no_state(self, mocks):
        state_queue, outgoing_queue = mocks
        state_queue.configure_mock(**{'get.side_effect': Empty})
        status_handler = StatusHandler()
        status_handler._handle_state_change()
        assert self.expected_original_state == status_handler.state
        outgoing_queue.put.assert_called_with(
            OutgoingMessage(STATUS, pickle.dumps(self.expected_original_state))
        )
