import pickle
from queue import Empty, Queue
from threading import Lock

from pytest import fixture

from bfgg.agent.actors.status_handler import StatusHandler
from bfgg.agent.state import State, StateData
from bfgg.utils.agentstatus import AgentStatus
from bfgg.utils.messages import STATUS, OutgoingMessage


class TestStatusHandler:

    new_state = StateData(
        status=AgentStatus.TEST_RUNNING,
        cloned_repos=None,
        test_running="test",
        test_id="1234",
        extra_info="interesting stuff",
        group=None,
    )

    expected_new_state = StateData(
        status=AgentStatus.TEST_RUNNING,
        cloned_repos=set(),
        test_running="test",
        test_id="1234",
        extra_info="interesting stuff",
        group="ungrouped",
    )

    expected_original_state = StateData(
        status=AgentStatus.AVAILABLE,
        cloned_repos=set(),
        test_running="",
        test_id="",
        extra_info="",
        group="ungrouped",
    )

    @fixture()
    def mocks(self, mocker):
        outgoing_queue = Queue()
        mocker.spy(outgoing_queue, "put")
        state = State(Lock())
        mocker.spy(state, "update")
        yield outgoing_queue, state

    def test_handle_state_change_new_state(self, mocks):
        outgoing_queue, state = mocks
        state_queue = Queue()
        state_queue.put(self.new_state)

        status_handler = StatusHandler(state, state_queue, outgoing_queue)
        status_handler._handle_state_change()
        state.update.assert_called_with(self.new_state)
        outgoing_queue.put.assert_called_with(
            OutgoingMessage(STATUS, pickle.dumps(self.expected_new_state))
        )

    def test_handle_state_change_no_state(self, mocks, mocker):
        outgoing_queue, state = mocks
        state_queue = mocker.MagicMock(spec=Queue)
        state_queue.configure_mock(**{"get.side_effect": Empty})

        status_handler = StatusHandler(state, state_queue, outgoing_queue)
        status_handler._handle_state_change()
        state_queue.assert_not_called()
        outgoing_queue.put.assert_called_with(
            OutgoingMessage(STATUS, pickle.dumps(self.expected_original_state))
        )
