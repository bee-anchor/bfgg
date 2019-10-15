import threading
import os
from concurrent import futures
import zmq
import subprocess
import logging
from pathlib import Path
from bfgg.utils.messages import CLONE, START_TEST, STOP_TEST
from bfgg.agent.state import State


logger = logging.getLogger(__name__)

class TaskHandler(threading.Thread):

    def __init__(self, lock: threading.Lock, state: State, context: zmq.Context, controller_host: str, port: str, results_folder: str, gatling_location: str):
        threading.Thread.__init__(self)
        self.lock = lock
        self.state = state
        self.context = context
        self.controller_host = controller_host
        self.port = port
        self.results_folder = results_folder
        self.gatling_location = gatling_location
        self.test_process = None

    def run(self):
        handler = self.context.socket(zmq.PULL)
        handler.connect(f"tcp://{self.controller_host}:{self.port}")
        logger.info("TaskHandler thread started")
        while True:
            try:
                [type, identity, message] = handler.recv_multipart()
                if type == CLONE:
                    self.clone_repo(message.decode("utf-8"))
                elif type == START_TEST:
                    project, test = message.decode('utf-8').split(",")
                    self.start_test(project, test)
                elif type == STOP_TEST:
                    self.stop_test()
                else:
                    print(type, identity, message)
            except Exception as e:
                logger.error(e)
                continue

    def clone_repo(self, project: str):
        project_name = project[project.find('/') + 1: project.find('.git')]
        logger.info(f"Getting {project}")
        resp = subprocess.Popen(['git', 'clone', project],
                                cwd=str(Path.home()),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        stdout, stderror = resp.communicate()
        stdout = stdout.decode('utf-8')
        if f"Cloning into '{project_name}'" in stdout:
            with self.lock:
                self.state.status = "Cloned"
            logger.info(f"Cloned {project_name}")
        elif f"already exists and is not an empty directory" in stdout:
            resp = subprocess.Popen(['git', 'pull'],
                                    cwd=f"{str(Path.home())}/{project_name}",
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            stdout, stderror = resp.communicate()
            stdout = stdout.decode('utf-8')
            with self.lock:
                self.state.status = "Cloned"
            logger.info(f"Got latest {project_name}")
        logger.debug(stdout)

    def start_test(self, project: str, test: str):
        logger.info([f'{self.gatling_location}/bin/gatling.sh', '-nr', '-sf', f'{str(Path.home())}/{project}/src', '-s', test, '-rf', self.results_folder],)
        self.test_process = subprocess.Popen([f'{self.gatling_location}/bin/gatling.sh', '-nr', '-sf', f'{str(Path.home())}/{project}/src', '-s', test, '-rf', self.results_folder],
                                             cwd=f'{str(Path.home())}/{project}',
                                             preexec_fn=os.setsid,
                                             stdin=subprocess.PIPE,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.STDOUT)
        executor = futures.ThreadPoolExecutor(max_workers=1)
        while True:
            line_getter = executor.submit(self.test_process.stdout.readline)
            try:
                line = line_getter.result(timeout=30)
            except futures.TimeoutError:
                self.test_process.terminate()
                with self.lock:
                    self.state.status = "Cloned"
                logger.error("gatling output ended unexpectedly, gatling process terminated")
                break
            else:
                logger.debug(line.decode('utf-8').rstrip())
                if line == b'':
                    self.test_process.terminate()
                    logger.error("gatling output ended unexpectedly, gatling process terminated")
                    break
                elif f"Simulation {test} started".encode('utf-8') in line:
                    with self.lock:
                        self.state.status = "Test_Running"
                    logger.info(f"Test {test} started")
                elif b"No tests to run for Gatling" in line:
                    self.test_process.terminate()
                    logger.error(f"No test was run, check the test class provided: {test}")
                    break
                elif f"Simulation {test} completed".encode('utf-8') in line:
                    self.test_process.terminate()
                    with self.lock:
                        self.state.status = "Test_Finished"
                    logger.info(f"Test {test} finished!")
                    break

    def stop_test(self):
        if self.test_process.poll() is None:
            self.test_process.terminate()
            with self.lock:
                self.state.status = "Cloned"
            logger.info("Stopped test")
