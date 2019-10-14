import threading
import zmq
from bfgg.controller.state import State

STATE = State()
LOCK = threading.Lock()
CONTEXT = zmq.Context()
