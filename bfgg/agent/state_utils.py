from queue import Queue
from bfgg.utils.messages import OutgoingMessage, START_TEST, FINISHED_TEST
from bfgg.utils.agentstatus import AgentStatus
from bfgg.agent.state import StateData


def handle_state_change_partial(state_queue: Queue, outgoing_queue: Queue):
    def __handle_state_change(status: AgentStatus = None, cloned_repo: set = None,
                              test_running: str = None, test_id: str = None, extra_info: str = None,
                              group: str = None):
        state_changes = StateData(status, cloned_repo, test_running, test_id, extra_info, group)
        state_queue.put(state_changes)
        # allow the controller to know these specific state changes for handling report generation
        if status == AgentStatus.TEST_RUNNING:
            outgoing_queue.put(OutgoingMessage(START_TEST, test_id.encode('utf-8')))
        elif status == AgentStatus.TEST_FINISHED:
            outgoing_queue.put(OutgoingMessage(FINISHED_TEST, test_id.encode('utf-8')))

    return __handle_state_change
