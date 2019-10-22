import os
import shutil
import threading
import subprocess
import zmq
import logging
import boto3
from datetime import datetime
from bfgg.controller.state import State
from bfgg.utils.messages import START_RESULTS, RESULT


logger = logging.getLogger(__name__)


class ResultsGetter:

    CHUNK_SIZE = 250000
    PIPELINE = 10

    def __init__(self, lock: threading.Lock, context: zmq.Context, port, state: State, results_folder, gatling_location, s3_bucket, s3_region):
        self.lock = lock
        self.context = context
        self.port = port
        self.state: State = state
        self.results_folder = results_folder
        self.gatling_location = gatling_location
        self.s3_bucket = s3_bucket
        self.s3_region = s3_region

    def _reset_results_folder(self):
        if not os.path.exists(self.results_folder):
            os.mkdir(self.results_folder)
        else:
            print(os.listdir(self.results_folder))
            for i in os.listdir(self.results_folder):
                if os.path.isfile(os.path.join(self.results_folder, i)):
                    os.remove(os.path.join(self.results_folder, i))
                elif os.path.isdir(os.path.join(self.results_folder, i)):
                    shutil.rmtree(os.path.join(self.results_folder, i))

    @staticmethod
    def _send_recv_start_message(socket, agent):
        logger.debug([
            START_RESULTS,
            b"controller",
            b"Send latest",
        ])
        socket.send_multipart([
            START_RESULTS,
            b"controller",
            b"Send latest",
        ])
        logger.debug("Start message sent")
        resp = socket.recv_multipart()
        logger.debug(resp)
        [type, ip, message] = resp
        assert ip == agent and message == b"OK"

    def _send_chunk_message(self, socket, offset):
        logger.debug([
            RESULT,
            b"controller",
            str(offset).encode('utf-8'),
            str(self.CHUNK_SIZE).encode('utf-8')
        ])
        socket.send_multipart([
            RESULT,
            b"controller",
            str(offset).encode('utf-8'),
            str(self.CHUNK_SIZE).encode('utf-8')
        ])
        logger.debug("Chunk message sent")

    @staticmethod
    def _get_chunk(socket):
        try:
            chunk = socket.recv_multipart()
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                return  # shutting down, quit

            else:
                raise
        logger.debug("Chunk received")
        return chunk[0]

    def _data_getter_loop(self, socket, file, agent: str):
        credit = self.PIPELINE  # Up to PIPELINE chunks in transit
        total = 0  # Total bytes received
        chunks = 0  # Total chunks received
        offset = 0  # Offset of next chunk request
        while True:
            while credit:
                # ask for next chunk
                self._send_chunk_message(socket, offset)

                offset += self.CHUNK_SIZE
                credit -= 1

            chunk = self._get_chunk(socket)

            file.write(chunk.decode('utf-8'))

            chunks += 1
            credit += 1
            size = len(chunk)
            total += size
            if size < self.CHUNK_SIZE:
                logger.info(f"Result retrieval completed for {agent}")
                socket.close()
                break

    @staticmethod
    def _content_type_from_file(filename: str):
        content_types = {
            "html": "text/html",
            "png": "image/png",
            "css": "text/css",
            "jpg": "image/jpeg",
            "js": "application/javascript",
            "json": "application/json",
            "xml": "application/xml",
            "ico": "image/x-icon",
            "log": "text/plain",
            "svg": "image/svg+xml"
        }

        type = filename.split('.')[-1]
        return content_types[type]

    def _upload_results(self):

        folder = datetime.now().strftime("%Y%m%d_%H%M")
        s3 = boto3.resource('s3', region_name=self.s3_region)

        for file in os.listdir(self.results_folder):
            path = os.path.join(self.results_folder, file)
            if os.path.isfile(path):
                with open(path, "rb") as opened_file:
                    s3.Bucket(self.s3_bucket).put_object(Key=f"{folder}/{file}", Body=opened_file.read(), ACL='private', ContentType=self._content_type_from_file(file))
            elif os.path.isdir(path):
                # report created only has one level of nesting
                for sub_file in os.listdir(os.path.join(self.results_folder, file)):
                    with open(os.path.join(path, sub_file), "rb") as opened_file:
                        s3.Bucket(self.s3_bucket).put_object(Key=f"{folder}/{file}/{sub_file}", Body=opened_file.read(), ACL='private', ContentType=self._content_type_from_file(sub_file))

        url = f'https://{self.s3_bucket}.s3.amazonaws.com/{folder}/index.html'
        return url

    def get_results(self):
        self._reset_results_folder()
        with self.lock:
            current_agents = self.state.connected_agents

        for agent in current_agents:
            getter = self.context.socket(zmq.DEALER)
            getter.set_hwm(self.PIPELINE)
            str_agent = agent.decode('utf-8')
            logger.info(f"Starting receiving results from {str_agent}")
            getter.setsockopt(zmq.IDENTITY, agent)
            getter.connect(f"tcp://{str_agent}:{self.port}")

            self._send_recv_start_message(getter, agent)

            with open(os.path.join(self.results_folder, str_agent.replace('.', '_')) + '.log', "w+") as f:
                self._data_getter_loop(getter, f, str_agent)

        logger.info([f'{self.gatling_location}/bin/gatling.sh', '-ro', self.results_folder])
        report_process = subprocess.Popen(
            [f'{self.gatling_location}/bin/gatling.sh', '-ro', self.results_folder],
            cwd=self.results_folder,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        stdout, stderror = report_process.communicate()
        stdout = stdout.decode('utf-8')
        logger.info(stdout)

        url = self._upload_results()
        return url
