from dataclasses import dataclass

STATUS = "STAT".encode('utf-8')
CLONE = "CLONE".encode('utf-8')
START_TEST = "START".encode('utf-8')
STOP_TEST = "STOP".encode('utf-8')
FINISHED_TEST = "FINISHED".encode('utf-8')
LOG = "LOG".encode('utf-8')
BYE = "BYE".encode('utf-8')


@dataclass
class OutgoingMessage:
    type: bytes
    details: bytes
