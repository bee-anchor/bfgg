import os
import signal
import subprocess
from collections import deque
from queue import Queue
from threading import Thread
from time import sleep
import logging

from bfgg.agent.utils import AgentUtils
from bfgg.agent.actors.log_follower import LogFollower
from bfgg.utils.agentstatus import AgentStatus


class GatlingRunner(Thread):
    def __init__(
        self,
        gatling_location: str,
        tests_location: str,
        results_folder: str,
        test_id: str,
        project: str,
        test: str,
        java_opts: str,
        outgoing_queue: Queue,
        log_send_interval: float,
        agent_utils: AgentUtils,
        logger=logging.getLogger(__name__),
    ):
        super().__init__()
        self.logger = logger
        self.gatling_location = gatling_location
        self.tests_location = tests_location
        self.results_folder = results_folder
        self.test_id = test_id
        self.project = project
        self.test = test
        self.java_opts = java_opts
        self.outgoing_queue = outgoing_queue
        self.agent_utils = agent_utils
        self.log_send_interval = log_send_interval
        self.stop_runner = False
        self.test_process = None
        self.log_follower = None
        self.is_running = False

    def _start_test_process(self):
        environ = os.environ.copy()
        if self.java_opts != "":
            self.logger.info(self.java_opts)
            environ["JAVA_OPTS"] = self.java_opts
        self.logger.info(
            [
                f"{self.gatling_location}/bin/gatling.sh",
                "-nr",
                "-sf",
                f"{self.tests_location}/{self.project}/src",
                "-s",
                self.test,
                "-rf",
                self.results_folder,
            ],
        )
        try:
            test_process = subprocess.Popen(
                [
                    f"{self.gatling_location}/bin/gatling.sh",
                    "-nr",
                    "-sf",
                    f"{self.tests_location}/{self.project}/src",
                    "-s",
                    self.test,
                    "-rf",
                    self.results_folder,
                ],
                cwd=f"{self.tests_location}/{self.project}",
                env=environ,
                preexec_fn=os.setsid,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.test_process = test_process
            return test_process
        except FileNotFoundError as e:
            self._handle_error(
                f"{str(e)}\nCheck project requested OR configured gatling location"
            )

    def _handle_process(self, test_process):
        latest_lines = deque(maxlen=10)
        while self.is_running:
            sleep(0.5)
            line = test_process.stdout.readline()
            while len(line) > 0:
                line = line.decode("utf-8")
                latest_lines.append(line)
                self._handle_process_output(line)
                line = test_process.stdout.readline()
            if self.is_running and self.stop_runner:
                self._stop_test()
            if self.is_running and test_process.poll() is not None:
                log_lines = "\n".join(latest_lines)
                self._handle_error(
                    f"Gatling process ended unexpectedly, last log lines:\n {log_lines}"
                )

    def _handle_process_output(self, line):
        self.logger.debug(line.rstrip())
        if f"Simulation {self.test} started" in line:
            self.agent_utils.handle_state_change(
                status=AgentStatus.TEST_RUNNING,
                test_running=f"{self.project} - {self.test}",
                test_id=self.test_id,
            )
            self.logger.info(f"Test {self.test} started")
            self.log_follower = LogFollower(
                self.results_folder, self.outgoing_queue, self.log_send_interval
            )
            self.log_follower.name = f"LogFollower_{self.test}"
            self.log_follower.daemon = True
            self.log_follower.start()
        elif "No tests to run for Gatling" in line:
            self._handle_error(
                f"No test was run, check the test class provided: {self.test}"
            )
        elif f"Simulation {self.test} completed" in line:
            self._stop_processes()
            self.agent_utils.handle_state_change(
                status=AgentStatus.TEST_FINISHED, test_running="", test_id=self.test_id
            )
            self.logger.info(f"Test {self.test} finished!")

    def run(self):
        test_process = self._start_test_process()
        os.set_blocking(test_process.stdout.fileno(), False)
        self.is_running = True
        self._handle_process(test_process)

    def _stop_processes(self):
        try:
            if self.test_process:
                os.killpg(os.getpgid(self.test_process.pid), signal.SIGTERM)
                self.test_process.terminate()
        except ProcessLookupError:
            self.logger.warning("Process ended unexpectedly - Gatling may have crashed")
        if self.log_follower:
            self.log_follower.stop_thread = True
        self.is_running = False

    def _stop_test(self):
        self._stop_processes()
        self.agent_utils.handle_state_change(
            status=AgentStatus.TEST_STOPPED, test_running=""
        )
        self.logger.info("Test manually stopped")
        self.is_running = False

    def _handle_error(self, msg):
        self._stop_processes()
        self.agent_utils.handle_state_change(
            status=AgentStatus.ERROR, test_running="", extra_info=msg
        )
        self.logger.error(msg)
        self.is_running = False
