import os
import threading
import subprocess
import zmq
import logging.config
import boto3
from datetime import datetime
from bfgg.utils.messages import START_RESULTS, RESULT
from bfgg.utils.helpers import create_or_empty_folder
from bfgg.controller.model import STATE


class ResultsGetter:

    CHUNK_SIZE = 250000

    def __init__(self, lock: threading.Lock, context: zmq.Context, port: str, results_folder: str,
                 gatling_location: str, s3_bucket: str, s3_region: str):
        self.lock = lock
        self.context = context
        self.port = port
        self.results_folder = results_folder
        self.gatling_location = gatling_location
        self.s3_bucket = s3_bucket
        self.s3_region = s3_region

    @staticmethod
    def _send_recv_start_message(socket, agent):
        logging.debug([
            START_RESULTS,
            b"controller",
            b"Send latest",
        ])
        socket.send_multipart([
            START_RESULTS,
            b"controller",
            b"Send latest",
        ])
        logging.debug("Start message sent")
        resp = socket.recv_multipart()
        logging.debug(resp)
        [type, ip, message] = resp
        assert ip == agent and message == b"OK"

    def _send_chunk_message(self, socket, offset):
        logging.debug([
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
        logging.debug("Chunk message sent")

    @staticmethod
    def _get_chunk(socket):
        try:
            chunk = socket.recv_multipart()
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                return  # shutting down, quit

            else:
                raise
        logging.debug("Chunk received")
        return chunk[0]

    def _data_getter_loop(self, socket, file, agent: str):
        total = 0  # Total bytes received
        chunks = 0  # Total chunks received
        offset = 0  # Offset of next chunk request
        while True:
            self._send_chunk_message(socket, offset)
            chunk = self._get_chunk(socket)
            file.write(chunk.decode('utf-8'))

            chunks += 1
            offset += self.CHUNK_SIZE
            size = len(chunk)
            total += size
            if size < self.CHUNK_SIZE:
                logging.info(f"Result retrieval completed for {agent}")
                logging.info(f"Bytes sent: {total}")
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
        create_or_empty_folder(self.results_folder)
        current_agents = STATE.connected_agents

        for agent in current_agents:
            getter = self.context.socket(zmq.DEALER)
            str_agent = agent.decode('utf-8')
            logging.info(f"Starting receiving results from {str_agent}")
            getter.setsockopt(zmq.IDENTITY, agent)
            getter.connect(f"tcp://{str_agent}:{self.port}")

            self._send_recv_start_message(getter, agent)

            with open(os.path.join(self.results_folder, str_agent.replace('.', '_')) + '.log', "w+") as f:
                self._data_getter_loop(getter, f, str_agent)

        logging.info([f'{self.gatling_location}/bin/gatling.sh', '-ro', self.results_folder])
        report_process = subprocess.Popen(
            [f'{self.gatling_location}/bin/gatling.sh', '-ro', self.results_folder],
            cwd=self.results_folder,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        stdout, stderror = report_process.communicate()
        stdout = stdout.decode('utf-8')
        logging.info(stdout)

        url = self._upload_results()
        return url
