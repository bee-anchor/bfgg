import threading
import os
from concurrent import futures
import subprocess
import signal
from bfgg.agent.actors.log_follower import LogFollower
from bfgg.utils.agentstatus import AgentStatus
from bfgg.utils.logging import logger
from bfgg.agent.model import handle_state_change


class GatlingRunner(threading.Thread):

    def __init__(self, gatling_location: str, tests_location: str, results_folder: str, test_id: str, project: str, test: str,
                 java_opts: str):
        threading.Thread.__init__(self)
        self.logger = logger
        self.gatling_location = gatling_location
        self.tests_location = tests_location
        self.results_folder = results_folder
        self.test_id = test_id
        self.project = project
        self.test = test
        self.java_opts = java_opts
        self.stop_runner = False
        self.test_process = None
        self.log_follower = None
        self.is_running = False

    def _start_test_process(self):
        environ = os.environ.copy()
        if self.java_opts != '':
            self.logger.info(self.java_opts)
            environ['JAVA_OPTS'] = self.java_opts
        self.logger.info(
            [f'{self.gatling_location}/bin/gatling.sh', '-nr', '-sf', f'{self.tests_location}/{self.project}/src', '-s',
             self.test, '-rf', self.results_folder], )
        try:
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
        except FileNotFoundError:
            self._handle_error(f"FileNotFoundError - {self.tests_location}/{self.project}: Check project requested")

    def _handle_process(self, test_process):
        executor = futures.ThreadPoolExecutor(max_workers=1)
        while self.is_running:
            if self.stop_runner:
                self._stop_test()
            line_getter = executor.submit(test_process.stdout.readline)
            try:
                line = line_getter.result(timeout=30)
            except futures.TimeoutError:
                self._handle_error("No output from gatling for 30s, gatling process terminated")
            else:
                self._handle_process_output(line)

    def _handle_process_output(self, line):
        self.logger.debug(line.decode('utf-8').rstrip())
        if line == b'':
            self._handle_error(f"Gatling output ended unexpectedly, gatling process terminated: {self.test}")
        elif f"Simulation {self.test} started".encode('utf-8') in line:
            handle_state_change(status=AgentStatus.TEST_RUNNING, test_running=f"{self.project} - {self.test}",
                                test_id=self.test_id)
            self.logger.info(f"Test {self.test} started")
            self.log_follower = LogFollower(self.results_folder)
            self.log_follower.name = f"LogFollower_{self.test}"
            self.log_follower.daemon = True
            self.log_follower.start()
        elif b"No tests to run for Gatling" in line:
            self._handle_error(f"No test was run, check the test class provided: {self.test}")
        elif f"Simulation {self.test} completed".encode('utf-8') in line:
            self._stop_processes()
            handle_state_change(status=AgentStatus.TEST_FINISHED, test_running="", test_id=self.test_id)
            self.logger.info(f"Test {self.test} finished!")

    def run(self):
        test_process = self._start_test_process()
        self.is_running = True
        self._handle_process(test_process)

    def _stop_processes(self):
        try:
            if self.test_process:
                os.killpg(os.getpgid(self.test_process.pid), signal.SIGTERM)
                self.test_process.terminate()
        except ProcessLookupError:
            self.logger.warning("Process has already been terminated - Gatling may have crashed")
        if self.log_follower:
            self.log_follower.stop_thread = True
        self.is_running = False

    def _stop_test(self):
        self._stop_processes()
        handle_state_change(status=AgentStatus.TEST_STOPPED, test_running="")
        self.logger.info("Test manually stopped")
        self.is_running = False

    def _handle_error(self, msg):
        self._stop_processes()
        handle_state_change(status=AgentStatus.ERROR, test_running="",
                            extra_info=msg)
        self.logger.error(msg)
        self.is_running = False
