import threading
import os
from concurrent import futures
import zmq
import subprocess
import logging.config
from bfgg.utils.messages import CLONE, START_TEST, STOP_TEST
from bfgg.agent.state import State


class TaskHandler(threading.Thread):

    def __init__(self, lock: threading.Lock, state: State, context: zmq.Context, controller_host: str, port: str,
                 tests_location: str, results_folder: str, gatling_location: str):
        threading.Thread.__init__(self)
        self.lock = lock
        self.state = state
        self.context = context
        self.controller_host = controller_host
        self.port = port
        self.tests_location = tests_location
        self.results_folder = results_folder
        self.gatling_location = gatling_location
        self.test_process = None

    def run(self):
        handler = self.context.socket(zmq.PULL)
        handler.connect(f"tcp://{self.controller_host}:{self.port}")
        logging.info("TaskHandler thread started")
        while True:
            try:
                [type, identity, message] = handler.recv_multipart()
                if type == CLONE:
                    self.clone_repo(message.decode("utf-8"))
                elif type == START_TEST:
                    project, test, java_opts = message.decode('utf-8').split(",")
                    self.start_test(project, test, java_opts)
                elif type == STOP_TEST:
                    self.stop_test()
                else:
                    print(type, identity, message)
            except Exception as e:
                logging.error(e)
                continue

    def clone_repo(self, project: str):
        project_name = project[project.find('/') + 1: project.find('.git')]
        logging.info(f"Getting {project}")
        resp = subprocess.Popen(['git', 'clone', project],
                                cwd=self.tests_location,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        stdout, stderror = resp.communicate()
        stdout = stdout.decode('utf-8')
        if f"Cloning into '{project_name}'" in stdout:
            with self.lock:
                self.state.status = "Cloned"
            logging.info(f"Cloned {project_name}")
        elif f"already exists and is not an empty directory" in stdout:
            command = (f"git -C {os.path.join(self.tests_location, project_name)} fetch && "
                       f"git -C {os.path.join(self.tests_location, project_name)} reset origin/master --hard")
            resp = subprocess.Popen(command,
                                    shell=True,
                                    cwd=f"{self.tests_location}/{project_name}",
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            stdout, stderror = resp.communicate()
            stdout = stdout.decode('utf-8')
            with self.lock:
                self.state.status = "Cloned"
            logging.info(f"Got latest {project_name}")
        logging.debug(stdout)

    def start_test(self, project: str, test: str, java_opts: str):
        environ = os.environ.copy()
        if java_opts != '':
            logging.info(java_opts)
            environ['JAVA_OPTS'] = java_opts
        logging.info([f'{self.gatling_location}/bin/gatling.sh', '-nr', '-sf', f'{self.tests_location}/{project}/src', '-s', test, '-rf', self.results_folder],)
        self.test_process = subprocess.Popen([f'{self.gatling_location}/bin/gatling.sh', '-nr', '-sf', f'{self.tests_location}/{project}/src', '-s', test, '-rf', self.results_folder],
                                             cwd=f'{self.tests_location}/{project}',
                                             env=environ,
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
                logging.error("gatling output ended unexpectedly, gatling process terminated")
                break
            else:
                logging.debug(line.decode('utf-8').rstrip())
                if line == b'':
                    self.test_process.terminate()
                    logging.error("gatling output ended unexpectedly, gatling process terminated")
                    break
                elif f"Simulation {test} started".encode('utf-8') in line:
                    with self.lock:
                        self.state.status = "Test_Running"
                    logging.info(f"Test {test} started")
                elif b"No tests to run for Gatling" in line:
                    self.test_process.terminate()
                    logging.error(f"No test was run, check the test class provided: {test}")
                    break
                elif f"Simulation {test} completed".encode('utf-8') in line:
                    self.test_process.terminate()
                    with self.lock:
                        self.state.status = "Test_Finished"
                    logging.info(f"Test {test} finished!")
                    break

    def stop_test(self):
        if self.test_process.poll() is None:
            self.test_process.terminate()
            with self.lock:
                self.state.status = "Cloned"
            logging.info("Stopped test")
