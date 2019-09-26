import time
import logging
import threading
import zmq

agents = []


class Registrator(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        context = zmq.Context()
        registrator = context.socket(zmq.REP)
        registrator.bind("tcp://*:9998")
        print("Registrator thread started")
        while True:
            [type, identity, message] = registrator.recv_multipart()
            print(type, identity, message)
            agents.append(identity)
            registrator.send_multipart([b"OK", b"Master", b"Hello"])
            time.sleep(1)


class Controller(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        context = zmq.Context()
        controller = context.socket(zmq.REQ)
        controller.bind("tcp://*:9999")
        print("Controller loop started")
        while True:
            for agent in agents:
                print(f"Sending heartbeat to {agent}")
                controller.send_multipart([b"HB", b"Master", b"Heartbeat"])
                [type, identity, message] = controller.recv_multipart()
                print(type, identity, message)
            time.sleep(10)


def main():
    registrator = Registrator()
    registrator.start()

    controller = Controller()
    controller.start()


if __name__ == "__main__":
    main()


