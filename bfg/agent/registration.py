import zmq
import threading
from bfg.utils.messages import REGISTRATION
from bfg.agent.state import State


def register(lock: threading.Lock, state: State, context: zmq.Context, controller_host: str, port: str):
    registrator = context.socket(zmq.REQ)
    registrator.connect(f"tcp://{controller_host}:{port}")
    print("Registering with controller")
    registrator.send_multipart([REGISTRATION, state.identity, b"Hello"])
    [type, identity, message] = registrator.recv_multipart()
    print("Registered")
    lock.acquire()
    state.status = "Registered"
    lock.release()
    registrator.close()