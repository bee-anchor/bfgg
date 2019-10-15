import os
import threading
import zmq
import logging
from bfgg.agent.state import State
from bfgg.utils.messages import START_RESULTS


logger = logging.getLogger(__name__)


class ResultsSender(threading.Thread):

    CHUNK_SIZE = 250000
    PIPELINE = 10

    def __init__(self, lock: threading.Lock, context: zmq.Context, port, state: State, results_folder):
        threading.Thread.__init__(self)
        self.lock = lock
        self.context = context
        self.port = port
        self.state: State = state
        self.results_folder = results_folder

    def _get_latest_logfile(self):
        result_folders = os.listdir(self.results_folder)
        folders = [os.path.join(self.results_folder, x) for x in result_folders if os.path.isdir(os.path.join(self.results_folder, x))]
        newest_folder = max(folders, key=os.path.getmtime)
        path = os.path.join(newest_folder, "simulation.log")
        print(path)
        return path

    def _send_start_message(self, identity, socket):
        logger.debug([identity, START_RESULTS, self.state.identity, b"OK"])
        socket.send_multipart([identity, START_RESULTS, self.state.identity, b"OK"])
        logger.debug("Start response sent")

    def _send_data_loop(self, identity, socket, file):
        # Start sending loop
        while True:
            # First frame in each message is the sender identity
            try:
                message = socket.recv_multipart()
                logger.debug("Send chunk message received")
                logger.debug(message)
                [identity, type, ip, offset, chunk] = message
            except zmq.ZMQError as e:
                if e.errno == zmq.ETERM:
                    break  # shutting down, quit
                else:
                    logger.error(e)
                    break

            offset = int(offset.decode('utf-8'))
            chunk = int(chunk.decode('utf-8'))

            # Read chunk of data from file
            file.seek(offset, os.SEEK_SET)
            data = file.read(chunk)

            # Send resulting chunk to client
            logger.debug("Sending log data")
            socket.send_multipart([identity, data])
            logger.debug("Log data sent")
            size = len(data)
            if size < chunk:
                logger.info("Finished sending result log")
                break


    def run(self):
        sender = self.context.socket(zmq.ROUTER)
        sender.set_hwm(self.PIPELINE)
        sender.bind(f"tcp://*:{self.port}")
        logger.info("ResultsSender thread started")

        while True:
            message = sender.recv_multipart()
            # ignore these if here: will be one of the batch of send chunk messages
            if len(message) == 5:
                continue
            # new message to start sending files
            else:
                [identity, type, ip, info] = message
            if type == START_RESULTS:
                logger.info("Starting sending results")
                self._send_start_message(identity, sender)
                file = open(self._get_latest_logfile(), "rb")
                self._send_data_loop(identity, sender, file)



