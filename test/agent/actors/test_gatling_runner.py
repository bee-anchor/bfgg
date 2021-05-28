from queue import Queue
from unittest import mock
from dataclasses import dataclass

from pytest import fixture

from bfgg.agent.actors.gatling_runner import GatlingRunner, subprocess, signal
from bfgg.utils.agentstatus import AgentStatus
from bfgg.agent.utils import AgentUtils

gatling_location = "/gatling"
tests_location = "/tests"
results_folder = "/results"
project = "project"
test = "test"
test_id = "1234"
java_opts = "-Xmx14G"
log_send_interval = 0.1


@dataclass
class Mocks:
    outgoing_queue: mock.MagicMock
    agent_utils: mock.MagicMock


@fixture
def setup():
    outgoing_queue = mock.create_autospec(Queue)
    agent_utils = mock.create_autospec(AgentUtils)
    gatling_runner = GatlingRunner(
        gatling_location,
        tests_location,
        results_folder,
        test_id,
        project,
        test,
        java_opts,
        outgoing_queue,
        log_send_interval,
        agent_utils,
    )
    return gatling_runner, Mocks(outgoing_queue, agent_utils)


def test_runner_start_process(setup, mocker):
    gatling_runner, _ = setup
    mock_subprocess = mocker.patch(
        "bfgg.agent.actors.gatling_runner.subprocess", autospec=True
    )
    result = gatling_runner._start_test_process()
    assert mock_subprocess.Popen.return_value == result


def test_runner_handle_process_output_ended_unexpectedly(setup, mocker):
    gatling_runner, _ = setup
    handle_error_mock = mocker.patch.object(GatlingRunner, "_handle_error")

    gatling_runner._handle_process_output(b"")

    handle_error_mock.assert_called_once_with(
        f"Gatling output ended unexpectedly, gatling process terminated: {test}"
    )


def test_runner_handle_process_output_simulation_started(setup, mocker):
    gatling_runner, mocks = setup
    stop_processes_mock = mocker.patch.object(GatlingRunner, "_stop_processes")
    mock_log_follower = mocker.patch(
        "bfgg.agent.actors.gatling_runner.LogFollower", autospec=True
    )

    gatling_runner._handle_process_output(f"Simulation {test} started".encode("utf-8"))

    mocks.agent_utils.handle_state_change.assert_called_once_with(
        status=AgentStatus.TEST_RUNNING,
        test_id=test_id,
        test_running=f"{project} - {test}",
    )
    stop_processes_mock.assert_not_called()
    assert mock_log_follower.return_value.daemon is True
    mock_log_follower.return_value.start.assert_called_once()


def test_runner_handle_process_output_no_tests(setup, mocker):
    gatling_runner, _ = setup
    handle_error_mock = mocker.patch.object(GatlingRunner, "_handle_error")

    gatling_runner._handle_process_output(b"No tests to run for Gatling")

    handle_error_mock.assert_called_once_with(
        f"No test was run, check the test class provided: {test}"
    )


def test_runner_handle_process_output_simulation_completed(setup, mocker):
    gatling_runner, mocks = setup
    stop_processes_mock = mocker.patch.object(GatlingRunner, "_stop_processes")

    gatling_runner._handle_process_output(
        f"Simulation {test} completed".encode("utf-8")
    )

    mocks.agent_utils.handle_state_change.assert_called_once_with(
        status=AgentStatus.TEST_FINISHED, test_id=test_id, test_running=""
    )
    stop_processes_mock.assert_called_once()


def test_runner_stop_processes(setup, mocker):
    gatling_runner, _ = setup
    mock_popen = mocker.patch.object(
        subprocess, "Popen", autospec=True, **{"pid": "PID"}
    )
    mock_os = mocker.patch(
        "bfgg.agent.actors.gatling_runner.os", **{"getpgid.return_value": "PGID"}
    )
    mock_log_follower = mocker.patch("bfgg.agent.actors.gatling_runner.LogFollower")

    gatling_runner.test_process = mock_popen
    gatling_runner.log_follower = mock_log_follower
    gatling_runner.is_running = True
    gatling_runner._stop_processes()

    mock_os.getpgid.assert_called_once_with("PID")
    mock_os.killpg.assert_called_once_with("PGID", signal.SIGTERM)
    mock_popen.terminate.assert_called_once()
    assert mock_log_follower.stop_thread is True
    assert gatling_runner.is_running is False


def test_runner_stop_test(setup, mocker):
    gatling_runner, mocks = setup
    stop_processes_mock = mocker.patch.object(GatlingRunner, "_stop_processes")

    gatling_runner.is_running = True
    gatling_runner._stop_test()

    stop_processes_mock.assert_called_once()
    mocks.agent_utils.handle_state_change.assert_called_once_with(
        status=AgentStatus.TEST_STOPPED, test_running=""
    )
    assert gatling_runner.is_running is False


def test_runner_handle_error(setup, mocker):
    gatling_runner, mocks = setup
    stop_processes_mock = mocker.patch.object(GatlingRunner, "_stop_processes")

    gatling_runner.is_running = True
    gatling_runner._handle_error("Error")

    stop_processes_mock.assert_called_once()
    mocks.agent_utils.handle_state_change.assert_called_once_with(
        status=AgentStatus.ERROR, extra_info="Error", test_running=""
    )
    assert gatling_runner.is_running is False
