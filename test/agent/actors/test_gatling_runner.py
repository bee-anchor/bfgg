from bfgg.agent.actors.gatling_runner import GatlingRunner, subprocess, signal
from bfgg.utils.agentstatus import AgentStatus

gatling_location = '/gatling'
tests_location = '/tests'
results_folder = '/results'
project = 'project'
test = 'test'
test_id = "1234"
java_opts = '-Xmx14G'


def test_runner_start_process(mocker):
    mock_subprocess = mocker.patch('bfgg.agent.actors.gatling_runner.subprocess', autospec=True)
    result = GatlingRunner(gatling_location, tests_location, results_folder, test_id, project, test,
                           java_opts)._start_test_process()
    assert mock_subprocess.Popen.return_value == result


def test_runner_handle_process_output_ended_unexpectedly(mocker):
    handle_error_mock = mocker.patch.object(GatlingRunner, '_handle_error')

    runner = GatlingRunner(gatling_location, tests_location, results_folder, test_id, project, test,
                           java_opts)
    runner._handle_process_output(b'')

    handle_error_mock.assert_called_once_with(f"Gatling output ended unexpectedly, gatling process terminated: {test}")


def test_runner_handle_process_output_simulation_started(mocker):
    stop_processes_mock = mocker.patch.object(GatlingRunner, '_stop_processes')
    state_mock = mocker.patch('bfgg.agent.actors.gatling_runner.handle_state_change')
    mock_low_follower = mocker.patch('bfgg.agent.actors.gatling_runner.LogFollower', autospec=True)

    runner = GatlingRunner(gatling_location, tests_location, results_folder, test_id, project, test,
                           java_opts)
    runner._handle_process_output(f"Simulation {test} started".encode('utf-8'))

    state_mock.assert_called_once_with(status=AgentStatus.TEST_RUNNING, test_id=test_id, test_running=f"{project} - {test}")
    stop_processes_mock.assert_not_called()
    assert mock_low_follower.return_value.daemon is True
    mock_low_follower.return_value.start.assert_called_once()


def test_runner_handle_process_output_no_tests(mocker):
    handle_error_mock = mocker.patch.object(GatlingRunner, '_handle_error')

    runner = GatlingRunner(gatling_location, tests_location, results_folder, test_id, project, test,
                           java_opts)
    runner._handle_process_output(b"No tests to run for Gatling")

    handle_error_mock.assert_called_once_with(f"No test was run, check the test class provided: {test}")


def test_runner_handle_process_output_simulation_completed(mocker):
    stop_processes_mock = mocker.patch.object(GatlingRunner, '_stop_processes')
    state_mock = mocker.patch('bfgg.agent.actors.gatling_runner.handle_state_change')

    runner = GatlingRunner(gatling_location, tests_location, results_folder, test_id, project, test,
                           java_opts)
    runner._handle_process_output(f"Simulation {test} completed".encode('utf-8'))

    state_mock.assert_called_once_with(status=AgentStatus.TEST_FINISHED, test_id=test_id, test_running='')
    stop_processes_mock.assert_called_once()


def test_runner_stop_processes(mocker):
    mock_popen = mocker.patch.object(subprocess, 'Popen', autospec=True, **{
        'pid': 'PID'
    })
    mock_os = mocker.patch('bfgg.agent.actors.gatling_runner.os', **{
        'getpgid.return_value': 'PGID'
    })
    mock_log_follower = mocker.patch('bfgg.agent.actors.gatling_runner.LogFollower')

    runner = GatlingRunner(gatling_location, tests_location, results_folder, test_id, project, test,
                           java_opts)
    runner.test_process = mock_popen
    runner.log_follower = mock_log_follower
    runner.is_running = True
    runner._stop_processes()

    mock_os.getpgid.assert_called_once_with('PID')
    mock_os.killpg.assert_called_once_with('PGID', signal.SIGTERM)
    mock_popen.terminate.assert_called_once()
    assert mock_log_follower.stop_thread is True
    assert runner.is_running is False


def test_runner_stop_test(mocker):
    stop_processes_mock = mocker.patch.object(GatlingRunner, '_stop_processes')
    state_mock = mocker.patch('bfgg.agent.actors.gatling_runner.handle_state_change')

    runner = GatlingRunner(gatling_location, tests_location, results_folder, test_id, project, test,
                           java_opts)
    runner.is_running = True
    runner._stop_test()

    stop_processes_mock.assert_called_once()
    state_mock.assert_called_once_with(status=AgentStatus.TEST_STOPPED, test_running='')
    assert runner.is_running is False


def test_runner_handle_error(mocker):
    stop_processes_mock = mocker.patch.object(GatlingRunner, '_stop_processes')
    state_mock = mocker.patch('bfgg.agent.actors.gatling_runner.handle_state_change')

    runner = GatlingRunner(gatling_location, tests_location, results_folder, test_id, project, test,
                           java_opts)
    runner.is_running = True
    runner._handle_error('Error')

    stop_processes_mock.assert_called_once()
    state_mock.assert_called_once_with(status=AgentStatus.ERROR, extra_info='Error', test_running='')
    assert runner.is_running is False
