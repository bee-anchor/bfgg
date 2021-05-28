import threading
from datetime import datetime

from pytest import fixture

from bfgg.agent.state import StateData
from bfgg.controller.state import Agent, State
from bfgg.utils.agentstatus import AgentStatus


class TestAgent:
    def test_update(self):
        now = int(datetime.now().timestamp()) - 10
        agent = Agent(StateData(AgentStatus.AVAILABLE, set(), "", "", "", "info"), now)
        agent.update(
            StateData(AgentStatus.TEST_RUNNING, {"repo"}, "test", "1234", "", "")
        )
        assert agent.state == StateData(
            AgentStatus.TEST_RUNNING, {"repo"}, "test", "1234", "", ""
        )
        assert agent.last_heard_from > now


class TestState:
    @fixture()
    def state(self):
        state: State = State(threading.Lock())
        state._current_agents = {
            b"A": Agent(
                StateData(AgentStatus.AVAILABLE, set(), "", "", "", "group1"), 123
            ),
            b"B": Agent(StateData(AgentStatus.AVAILABLE, set(), "", "", "", ""), 123),
            b"C": Agent(
                StateData(AgentStatus.AVAILABLE, set(), "", "", "", "group1"), 123
            ),
            b"D": Agent(
                StateData(AgentStatus.AVAILABLE, set(), "", "", "", "group2"), 123
            ),
        }
        yield state

    @fixture()
    def minimal_state(self):
        state: State = State(threading.Lock())
        state._current_agents = {
            b"A": Agent(
                StateData(AgentStatus.AVAILABLE, set(), "", "", "", "group1"), 123
            ),
        }
        yield state

    @fixture()
    def finished_state(self):
        state: State = State(threading.Lock())
        state._current_agents = {
            b"A": Agent(
                StateData(AgentStatus.TEST_FINISHED, set(), "", "", "", "group1"), 123
            ),
        }
        yield state

    @fixture()
    def group_not_finished_state(self):
        state: State = State(threading.Lock())
        state._current_agents = {
            b"A": Agent(
                StateData(AgentStatus.TEST_FINISHED, set(), "", "", "", "group1"), 123
            ),
            b"B": Agent(
                StateData(AgentStatus.TEST_RUNNING, set(), "", "", "", "group1"), 123
            ),
            b"C": Agent(
                StateData(AgentStatus.TEST_FINISHED, set(), "", "", "", "group2"), 123
            ),
        }
        yield state

    @fixture()
    def group_finished_state(self):
        state: State = State(threading.Lock())
        state._current_agents = {
            b"A": Agent(
                StateData(AgentStatus.TEST_FINISHED, set(), "", "", "", "group1"), 123
            ),
            b"B": Agent(
                StateData(AgentStatus.TEST_FINISHED, set(), "", "", "", "group1"), 123
            ),
            b"C": Agent(
                StateData(AgentStatus.TEST_RUNNING, set(), "", "", "", "group2"), 123
            ),
        }
        yield state

    def test_connected_agents(self, state):
        assert set(state.connected_agents) == {b"A", b"B", b"C", b"D"}

    def test_connected_agents_by_group(self, state):
        assert set(state.connected_agents_by_group("group1")) == {b"A", b"C"}

    def test_remove_agent(self, minimal_state):
        minimal_state.remove_agent(b"A")
        assert minimal_state._current_agents == {}

    def test_update_agent_state_new_agent(self, minimal_state):
        minimal_state.update_agent_state(
            b"B", StateData(AgentStatus.AVAILABLE, set(), "", "", "", "group2")
        )
        assert minimal_state._current_agents == {
            b"A": Agent(
                StateData(AgentStatus.AVAILABLE, set(), "", "", "", "group1"), 123
            ),
            b"B": Agent(
                StateData(AgentStatus.AVAILABLE, set(), "", "", "", "group2"),
                int(datetime.now().timestamp()),
            ),
        }

    def test_update_agent_state_existing_agent(self, minimal_state):
        minimal_state.update_agent_state(
            b"A",
            StateData(
                AgentStatus.TEST_RUNNING, set("repo"), "test", "1234", "", "group2"
            ),
        )
        assert minimal_state._current_agents == {
            b"A": Agent(
                StateData(
                    AgentStatus.TEST_RUNNING, set("repo"), "test", "1234", "", "group2"
                ),
                int(datetime.now().timestamp()),
            )
        }

    def test_current_agents_state(self, minimal_state):
        assert minimal_state.current_agents_state() == {
            b"A": StateData(AgentStatus.AVAILABLE, set(), "", "", "", "group1")
        }

    def test_current_agent_state_by_group(self, state):
        assert state.current_agents_state_by_group("group1") == {
            b"A": StateData(AgentStatus.AVAILABLE, set(), "", "", "", "group1"),
            b"C": StateData(AgentStatus.AVAILABLE, set(), "", "", "", "group1"),
        }

    def test_current_agent_state_list(self, minimal_state):
        assert minimal_state.current_agents_state_list() == [
            {
                "identity": "A",
                "status": "AVAILABLE",
                "cloned_repos": [],
                "test_running": "",
                "extra_info": "",
                "group": "group1",
            }
        ]

    def test_current_groups(self, state):
        assert set(state.current_groups()) == {"group1", "group2"}

    def test_all_agents_finished_false(self, state):
        assert state.all_agents_finished() is False

    def test_all_agents_finished_true(self, finished_state):
        assert finished_state.all_agents_finished() is True

    def test_all_agents_finished_in_group_false(self, group_not_finished_state):
        assert group_not_finished_state.all_agents_finished_in_group("group1") is False

    def test_all_agents_finished_in_group_true(self, group_finished_state):
        assert group_finished_state.all_agents_finished_in_group("group1") is True

    def test_handle_dead_agents(self, minimal_state, mocker):
        log_mock = mocker.patch("bfgg.controller.state.logger")
        minimal_state.handle_dead_agents()
        assert minimal_state._current_agents == {}
        log_mock.warning.assert_called_with(
            "Agent A has not been heard from for a while, removing from connected list"
        )
