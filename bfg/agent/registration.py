import zmq
from bfg.utils.messages import REGISTRATION


def register(identity: bytes, context: zmq.Context, controller_host: str, port: str):
    registrator = context.socket(zmq.REQ)
    registrator.connect(f"tcp://{controller_host}:{port}")
    print("Registering with controller")
    registrator.send_multipart([REGISTRATION, identity, b"Hello"])
    [type, identity, message] = registrator.recv_multipart()
    print(type, identity, message)
    registrator.close()
