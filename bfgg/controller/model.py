import threading
import zmq
from queue import Queue
from bfgg.controller.state import State

STATE = State()
LOCK = threading.Lock()
CONTEXT = zmq.Context()
OUTGOING_QUEUE = Queue()
