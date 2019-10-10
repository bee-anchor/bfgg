import threading
import os
import signal
from concurrent import futures
import zmq
import subprocess
import logging
from pathlib import Path
from bfgg.utils.messages import CLONE, PREP_TEST, START_TEST, STOP_TEST
from bfgg.agent.state import State


logger = logging.getLogger(__name__)


class TaskHandler(threading.Thread):

    def __init__(self, lock: threading.Lock, state: State, context: zmq.Context, controller_host: str, port: str):
        threading.Thread.__init__(self)
        self.lock = lock
        self.state = state
        self.context = context
        self.controller_host = controller_host
        self.port = port
        self.test_process = None
        self.project = None

    def run(self):
        handler = self.context.socket(zmq.PULL)
        handler.connect(f"tcp://{self.controller_host}:{self.port}")
        logger.info("TaskHandler thread started")
        while True:
            [type, identity, message] = handler.recv_multipart()
            if type == CLONE:
                self.clone_repo(message.decode("utf-8"))
            elif type == PREP_TEST:
                self.prepare_test()
            elif type == START_TEST:
                self.start_test(message.decode('utf-8'))
            elif type == STOP_TEST:
                self.stop_test()
            else:
                print(type, identity, message)

    def clone_repo(self, project: str):
        project_name = project[project.find('/') + 1: project.find('.git')]
        logger.info(f"Getting {project}")
        self.project = project
        resp = subprocess.Popen(['git', 'clone', f'{project}'],
                                cwd=str(Path.home()),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        stdout, stderror = resp.communicate()
        stdout = stdout.decode('utf-8')
        if f"Cloning into '{project}'" in stdout:
            with self.lock:
                self.state.status = "Cloned"
            logger.info(f"Cloned {project_name}")
        elif f"already exists and is not an empty directory" in stdout:
            resp = subprocess.Popen(['git', 'pull'],
                                    cwd=f"{str(Path.home())}/{project}",
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            stdout, stderror = resp.communicate()
            stdout = stdout.decode('utf-8')
            with self.lock:
                self.state.status = "Cloned"
            logger.info(f"Got latest {project_name}")
        logger.debug(stdout)

    def prepare_test(self):
        logger.info(f"Starting sbt for {self.project}")
        # creates process group for children as this spawns children that otherwise won't get any signals
        self.test_process = subprocess.Popen(['sbt'],
                                             cwd=f"{str(Path.home())}/{self.project}",
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
                # Have to terminate process this way to deal with the child process too
                os.killpg(self.test_process.pid, signal.SIGTERM)
                logger.error("got no output while trying to start sbt - try restarting agent")
                break
            else:
                logger.debug(line.decode('utf-8').rstrip())
                if b"sbt server started" in line:
                    with self.lock:
                        self.state.status = "Ready"
                    logger.info("SBT server started successfully")
                    break

    def start_test(self, test: str):
        command = b"gatling:testOnly " + test.encode('utf-8') + b"\n"
        self.test_process.stdin.write(command)
        self.test_process.stdin.flush()

        executor = futures.ThreadPoolExecutor(max_workers=1)
        while True:
            line_getter = executor.submit(self.test_process.stdout.readline)
            try:
                line = line_getter.result(timeout=30)
            except futures.TimeoutError:
                os.killpg(self.test_process.pid, signal.SIGTERM)
                with self.lock:
                    self.state.status = "Cloned"
                logger.error("sbt output ended unexpectedly, sbt process terminated")
                break
            else:
                logger.debug(line.decode('utf-8').rstrip())
                if f"Simulation {test} started".encode('utf-8') in line:
                    with self.lock:
                        self.state.status = "Test_Running"
                    logger.info(f"Test {test} started")
                elif b"No tests to run for Gatling" in line:
                    os.killpg(self.test_process.pid, signal.SIGTERM)
                    logger.error(f"No test was run, check the test class provided: {test}")
                    break
                elif b"[success]" in line:
                    os.killpg(self.test_process.pid, signal.SIGTERM)
                    with self.lock:
                        self.state.status = "Test_Finished"
                    logger.info(f"Test {test} finished!")
                    break

    def stop_test(self):
        if self.test_process.poll() is None:
            os.killpg(self.test_process.pid, signal.SIGTERM)
            with self.lock:
                self.state.status = "Cloned"
            logger.info("Stopped test")
