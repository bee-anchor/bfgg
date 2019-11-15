from dataclasses import dataclass

STATUS = "STAT".encode('utf-8')
CLONE = "CLONE".encode('utf-8')
START_TEST = "START".encode('utf-8')
STOP_TEST = "STOP".encode('utf-8')
LOG = "LOG".encode('utf-8')
BYE = "BYE".encode('utf-8')
START_RESULTS = "SRES".encode('utf-8')
RESULT = "RES".encode('utf-8')
CLONED_REPO = "CLONED".encode('utf-8')
TEST_RUNNING = "STARTED".encode('utf-8')
EXTRA_INFO = "XTRA".encode('utf-8')
AGENT_STATE = "AGST".encode('utf-8')
@dataclass
class OutgoingMessage:
    type: bytes
    details: bytes
