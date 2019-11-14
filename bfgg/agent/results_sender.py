# import os
# import threading
# import zmq
# import logging.config
# from bfgg.agent.state import State
# from bfgg.utils.messages import START_RESULTS
#
#
# class ResultsSender(threading.Thread):
#
#     CHUNK_SIZE = 250000
#
#     def __init__(self, lock: threading.Lock, context: zmq.Context, port, state: State, results_folder):
#         threading.Thread.__init__(self)
#         self.lock = lock
#         self.context = context
#         self.port = port
#         self.state: State = state
#         self.results_folder = results_folder
#
#     def _get_latest_logfile(self):
#         result_folders = os.listdir(self.results_folder)
#         folders = [os.path.join(self.results_folder, x) for x in result_folders if os.path.isdir(os.path.join(self.results_folder, x))]
#         newest_folder = max(folders, key=os.path.getmtime)
#         path = os.path.join(newest_folder, "simulation.log")
#         return path
#
#     def _send_start_message(self, identity, socket):
#         logging.debug([identity, START_RESULTS, self.state.identity, b"OK"])
#         socket.send_multipart([identity, START_RESULTS, self.state.identity, b"OK"])
#         logging.debug("Start response sent")
#
#     def _send_data_loop(self, identity, socket, file):
#         # Start sending loop
#         while True:
#             # First frame in each message is the sender identity
#             try:
#                 message = socket.recv_multipart()
#                 logging.debug("Send chunk message received")
#                 logging.debug(message)
#                 [identity, type, ip, offset, chunk] = message
#             except zmq.ZMQError as e:
#                 if e.errno == zmq.ETERM:
#                     break  # shutting down, quit
#                 else:
#                     logging.error(e)
#                     break
#
#             offset = int(offset.decode('utf-8'))
#             chunk = int(chunk.decode('utf-8'))
#
#             # Read chunk of data from file
#             file.seek(offset, os.SEEK_SET)
#             data = file.read(chunk)
#
#             # Send resulting chunk to client
#             logging.debug("Sending log data")
#             socket.send_multipart([identity, data])
#             logging.debug("Log data sent")
#             size = len(data)
#             if size < chunk:
#                 logging.info("Finished sending result log")
#                 break
#
#
#     def run(self):
#         sender = self.context.socket(zmq.ROUTER)
#         sender.bind(f"tcp://*:{self.port}")
#         logging.info("ResultsSender thread started")
#
#         while True:
#             message = sender.recv_multipart()
#             [identity, type, ip, info] = message
#             if type == START_RESULTS:
#                 logging.info("Starting sending results")
#                 self._send_start_message(identity, sender)
#                 file = open(self._get_latest_logfile(), "rb")
#                 self._send_data_loop(identity, sender, file)
#
#
#
