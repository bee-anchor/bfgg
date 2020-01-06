from bfgg.agent.state import State, StateData
from bfgg.utils.agentstatus import AgentStatus
from threading import Lock


def test_state_update():
    state = State(Lock())
    update_state_data = StateData(AgentStatus.TEST_RUNNING, {"test_repo"}, "test_1", "1234", None, None)
    state.update(update_state_data)
    assert state.state_data == StateData(AgentStatus.TEST_RUNNING, {"test_repo"}, "test_1", "1234", "", "ungrouped")
