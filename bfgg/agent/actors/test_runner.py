import threading
import os
from concurrent import futures
import subprocess
import signal
import logging.config
from bfgg.agent.actors.log_follower import LogFollower
from bfgg.utils.statuses import Statuses
from bfgg.agent.model import handle_state_change


class TestRunner(threading.Thread):

    def __init__(self, gatling_location: str, tests_location: str, results_folder: str, project: str, test: str,
                 java_opts: str):
        threading.Thread.__init__(self)
        self.gatling_location = gatling_location
        self.tests_location = tests_location
        self.results_folder = results_folder
        self.project = project
        self.test = test
        self.java_opts = java_opts
        self.stop_runner = False
        self.test_process = None
        self.log_follower = None

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
            if self.stop_runner:
                self._stop_test()
                break
            line_getter = executor.submit(test_process.stdout.readline)
            try:
                line = line_getter.result(timeout=30)
            except futures.TimeoutError:
                self._stop_processes()
                handle_state_change(status=Statuses.ERROR,
                                    extra_info="No output from gatling for 30s, gatling process terminated")
                break
            else:
                logging.debug(line.decode('utf-8').rstrip())
                if line == b'':
                    self._stop_processes()
                    handle_state_change(status=Statuses.ERROR,
                                        extra_info="Gatling output ended unexpectedly, gatling process terminated")
                    logging.error("gatling output ended unexpectedly, gatling process terminated")
                    break
                elif f"Simulation {self.test} started".encode('utf-8') in line:
                    handle_state_change(status=Statuses.TEST_RUNNING, test_running=f"{self.project} - {self.test}")
                    logging.info(f"Test {self.test} started")
                    self.log_follower = LogFollower(self.results_folder)
                    self.log_follower.daemon = True
                    self.log_follower.start()
                elif b"No tests to run for Gatling" in line:
                    self._stop_processes()
                    logging.error(f"No test was run, check the test class provided: {self.test}")
                    handle_state_change(status=Statuses.ERROR,
                                        extra_info="No test was ran, please check the test class provided")
                    break
                elif f"Simulation {self.test} completed".encode('utf-8') in line:
                    self._stop_processes()
                    handle_state_change(status=Statuses.TEST_FINISHED, test_running=None)
                    logging.info(f"Test {self.test} finished!")
                    break

    def run(self):
        test_process = self._start_test_process()
        self._handle_process_output(test_process)

    def _stop_processes(self):
        if self.test_process:
            os.killpg(os.getpgid(self.test_process.pid), signal.SIGTERM)
            self.test_process.terminate()
        if self.log_follower:
            self.log_follower.stop_thread = True

    def _stop_test(self):
        self._stop_processes()
        handle_state_change(status=Statuses.TEST_STOPPED)
        logging.info("Test manually stopped")
