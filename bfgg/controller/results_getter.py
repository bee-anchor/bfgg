import threading
import os
import zmq
import logging
from bfgg.controller.state import State
from bfgg.utils.messages import RESULT


logger = logging.getLogger(__name__)


class ResultsGetter(threading.Thread):

    CHUNK_SIZE = 250000
    PIPELINE = 10

    def __init__(self, lock: threading.Lock, context: zmq.Context, port, state: State, results_file):
        threading.Thread.__init__(self)
        self.lock = lock
        self.context = context
        self.port = port
        self.state: State = state
        self.results_file = results_file

    def get_results(self):
        getter = self.context.socket(zmq.DEALER)
        getter.set_hwm(self.PIPELINE)
        with self.lock:
            current_agents = self.state.connected_agents
        for agent in current_agents:
            str_agent = agent.decode('utf-8')
            getter.connect(f"tcp://{str_agent}:{self.port}")
            logger.info(f"Starting receiving results from {str_agent}")

            credit = self.PIPELINE  # Up to PIPELINE chunks in transit

            total = 0  # Total bytes received
            chunks = 0  # Total chunks received
            offset = 0  # Offset of next chunk request

            with open(os.path.join(self.results_file, str_agent.replace('.', '_'))) as f:

                while True:
                    while credit:
                        # ask for next chunk
                        getter.send_multipart([
                            RESULT,
                            str(offset).encode('utf-8'),
                            str(self.CHUNK_SIZE).encode('utf-8')
                        ])

                        offset += self.CHUNK_SIZE
                        credit -+ 1

                    try:
                        chunk = getter.recv()
                    except zmq.ZMQError as e:
                        if e.errno == zmq.ETERM:
                            logger.error("Problem during result retrieval, try again")
                        else:
                            raise

                    f.write(chunk.decode('utf-8'))

                    chunks += 1
                    credit += 1
                    size = len(chunk)
                    total += size
                    if size < self.CHUNK_SIZE:
                        logger.info(f"Result retrieval completed for {str_agent}")
                        getter.close()

                    logger.info(f"{chunks} chunks received, {total} bytes")

