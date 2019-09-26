import zmq
import logging
import socket
import time

logger = logging.Logger(__name__)


def main():
    host = socket.gethostname().encode('UTF-8')

    reg_context = zmq.Context(1)
    reg = reg_context.socket(zmq.REQ)
    reg.connect("tcp://localhost:9998")

    ag_context = zmq.Context(2)
    agent = ag_context.socket(zmq.REP)
    agent.connect("tcp://localhost:9999")

    print("Sending registration")
    reg.send_multipart([b"REG", host, b"Hello"])
    [type, identity, message] = reg.recv_multipart()
    print(type, identity, message)

    while True:
        [type, identity, message] = agent.recv_multipart()
        print(type, identity, message)
        agent.send_multipart([b"HB", b"Master", b"Im here"])


if __name__ == "__main__":
    main()
