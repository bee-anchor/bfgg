from dataclasses import dataclass
from enum import Enum

STATUS = "STAT".encode('utf-8')
CLONE = "CLONE".encode('utf-8')
START_TEST = "START".encode('utf-8')
STOP_TEST = "STOP".encode('utf-8')
FINISHED_TEST = "FINISHED".encode('utf-8')
LOG = "LOG".encode('utf-8')
BYE = "BYE".encode('utf-8')


class Statuses(Enum):
    ERROR = b'0'
    AVAILABLE = b'1'
    CLONED = b'2'
    TEST_RUNNING = b'3'
    TEST_STOPPED = b'4'
    TEST_FINISHED = b'5'

    @property
    def value(self) -> bytes:
        return super(Statuses, self).value


@dataclass
class OutgoingMessage:
    type: bytes
    details: bytes
