from enum import Enum


class AgentStatus(Enum):
    ERROR = b'0'
    AVAILABLE = b'1'
    TEST_RUNNING = b'2'
    TEST_STOPPED = b'3'
    TEST_FINISHED = b'4'
    CLONING = b'5'

    @property
    def value(self) -> bytes:
        return super(AgentStatus, self).value
