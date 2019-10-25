import threading
import os
from concurrent import futures
import subprocess
import logging.config
from bfgg.agent.state import State


class RunTest(threading.Thread):

    def __init__(self, lock: threading.Lock, state: State, gatling_location, tests_location, results_folder, project: str, test: str, java_opts: str):
        threading.Thread.__init__(self)
        self.lock = lock
        self.state = state
        self.gatling_location = gatling_location
        self.tests_location=tests_location
        self.results_folder=results_folder
        self.project = project
        self.test = test
        self.java_opts = java_opts
        self.test_process = None

    def _start_test_process(self):
        environ = os.environ.copy()
        if self.java_opts != '':
            logging.info(self.java_opts)
            environ['JAVA_OPTS'] = self.java_opts
        logging.info(
            [f'{self.gatling_location}/bin/gatling.sh', '-nr', '-sf', f'{self.tests_location}/{self.project}/src', '-s',
             self.test, '-rf', self.results_folder], )
        test_process = subprocess.Popen(
            [f'{self.gatling_location}/bin/gatling.sh', '-nr', '-sf', f'{self.tests_location}/{self.project}/src', '-s',
             self.test, '-rf', self.results_folder],
            cwd=f'{self.tests_location}/{self.project}',
            env=environ,
            preexec_fn=os.setsid,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        self.test_process = test_process
        return test_process

    def _handle_process_output(self, test_process):
        executor = futures.ThreadPoolExecutor(max_workers=1)
        while True:
            line_getter = executor.submit(test_process.stdout.readline)
            try:
                line = line_getter.result(timeout=30)
            except futures.TimeoutError:
                test_process.terminate()
                with self.lock:
                    self.state.status = "Test_Error"
                logging.error("no output from gatling for 30s, gatling process terminated")
                break
            else:
                logging.debug(line.decode('utf-8').rstrip())
                if line == b'':
                    test_process.terminate()
                    with self.lock:
                        self.state.status = "Test_Error"
                    logging.error("gatling output ended unexpectedly, gatling process terminated")
                    break
                elif f"Simulation {self.test} started".encode('utf-8') in line:
                    with self.lock:
                        self.state.status = "Test_Running"
                    logging.info(f"Test {self.test} started")
                elif b"No tests to run for Gatling" in line:
                    test_process.terminate()
                    logging.error(f"No test was run, check the test class provided: {self.test}")
                    break
                elif f"Simulation {self.test} completed".encode('utf-8') in line:
                    test_process.terminate()
                    with self.lock:
                        self.state.status = "Test_Finished"
                    logging.info(f"Test {self.test} finished!")
                    break

    def run(self):
        test_process = self._start_test_process()
        self._handle_process_output(test_process)

    def stop_test(self):
        if self.test_process is not None:
            os.killpg(os.getpgid(self.test_process.pid), 15)
            logging.info("Test manually stopped")
