import logging
import zmq
import threading
from concurrent import futures
from bfgg.utils.messages import REGISTRATION
from bfgg.agent.state import State


logger = logging.getLogger(__name__)

def register(lock: threading.Lock, state: State, context: zmq.Context, controller_host: str, port: str):
    registrator = context.socket(zmq.REQ)
    registrator.connect(f"tcp://{controller_host}:{port}")

    logger.info(f"Registering with controller - {controller_host}:{port}")
    registrator.send_multipart([REGISTRATION, state.identity, b"Hello"])

    executor = futures.ThreadPoolExecutor(max_workers=1)
    while True:
        receiver = executor.submit(registrator.recv_multipart)
        try:
            [type, identity, message] = receiver.result(timeout=5)
        except futures.TimeoutError:
            logger.error(f"Did not recieve registration confirmation message from Controller - is specified controller host ({controller_host}) correct?")
        else:
            logger.info("Registered")
            with lock:
                state.status = "Registered"
            break

    registrator.close()
