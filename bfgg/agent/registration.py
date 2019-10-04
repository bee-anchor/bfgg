import zmq
import threading
from concurrent import futures
from bfgg.utils.messages import REGISTRATION
from bfgg.agent.state import State


def register(lock: threading.Lock, state: State, context: zmq.Context, controller_host: str, port: str):
    registrator = context.socket(zmq.REQ)
    registrator.connect(f"tcp://{controller_host}:{port}")

    print("Registering with controller")
    registrator.send_multipart([REGISTRATION, state.identity, b"Hello"])

    executor = futures.ThreadPoolExecutor(max_workers=1)
    while True:
        reciever = executor.submit(registrator.recv_multipart)
        try:
            [type, identity, message] = reciever.result(timeout=5)
        except futures.TimeoutError:
            print("[ERROR] did not recieve registration confirmation message from Controller - is specified controller host correct?")
            break
        else:
            print("Registered")
            lock.acquire()
            state.status = "Registered"
            lock.release()
            break

    registrator.close()
