from dataclasses import dataclass
from typing import List

STATUS = "STAT".encode('utf-8')
CLONE = "CLONE".encode('utf-8')
START_TEST = "START".encode('utf-8')
STOP_TEST = "STOP".encode('utf-8')
FINISHED_TEST = "FINISHED".encode('utf-8')
LOG = "LOG".encode('utf-8')
BYE = "BYE".encode('utf-8')
START_RESULTS = "SRES".encode('utf-8')
RESULT = "RES".encode('utf-8')
GROUP = "GRP".encode('utf-8')


@dataclass
class OutgoingMessage:
    type: bytes
    details: bytes


@dataclass
class OutgoingMessageGrouped:
    type: bytes
    details: bytes
    group: bytes


@dataclass
class OutgoingMessageTargeted:
    type: bytes
    details: bytes
    targets: List[bytes]
