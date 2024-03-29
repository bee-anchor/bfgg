from bfgg.agent.message_handlers.incoming import IncomingMessageHandler
from bfgg.utils.messages import CLONE, START_TEST, STOP_TEST

controller_host = "localhost"
port = "8080"
tests_location = "/tests"
results_folder = "/results"
gatling_location = "/gatling"


def setup_mocks(mocker, return_value, return_type="return_value"):
    return mocker.patch(
        "bfgg.agent.message_handlers.incoming.zmq",
        **{f"socket.return_value.recv_multipart.{return_type}": return_value},
    )


def test_agent_incoming_message_handler_clone(mocker):
    zmq_mock = setup_mocks(mocker, (b"Identity", CLONE, b"Message"))
    clone_mock = mocker.patch("bfgg.agent.message_handlers.incoming.clone_repo")

    IncomingMessageHandler(
        zmq_mock,
        controller_host,
        port,
        tests_location,
        results_folder,
        gatling_location,
    )._message_handler_loop()

    zmq_mock.socket.return_value.recv_multipart.assert_called_once()
    clone_mock.assert_called_once()
    clone_mock.assert_called_with("Message", tests_location)


def test_agent_incoming_message_handler_start_test(mocker):
    zmq_mock = setup_mocks(
        mocker, (b"Identity", START_TEST, b"1234,Project,Test,Java opts")
    )
    test_runner_mock = mocker.patch(
        "bfgg.agent.message_handlers.incoming.GatlingRunner"
    )

    IncomingMessageHandler(
        zmq_mock,
        controller_host,
        port,
        tests_location,
        results_folder,
        gatling_location,
    )._message_handler_loop()

    zmq_mock.socket.return_value.recv_multipart.assert_called_once()
    test_runner_mock.assert_called_once()
    test_runner_mock.assert_called_with(
        gatling_location,
        tests_location,
        results_folder,
        "1234",
        "Project",
        "Test",
        "Java opts",
    )
    test_runner_mock.return_value.start.assert_called_once()


def test_agent_incoming_message_handler_stop_test_runner_exists(mocker):
    zmq_mock = setup_mocks(
        mocker,
        [
            (b"Identity", START_TEST, b"1234,Project,Test,Java opts"),
            (b"Identity", STOP_TEST, b"Stop"),
        ],
        "side_effect",
    )
    test_runner_mock = mocker.patch(
        "bfgg.agent.message_handlers.incoming.GatlingRunner"
    )

    message_handler = IncomingMessageHandler(
        zmq_mock,
        controller_host,
        port,
        tests_location,
        results_folder,
        gatling_location,
    )
    message_handler._message_handler_loop()
    message_handler._message_handler_loop()

    assert zmq_mock.socket.return_value.recv_multipart.call_count == 2
    assert test_runner_mock.return_value.stop_runner is True


def test_agent_incoming_message_handler_stop_test_runner_doesnt_exist(mocker):
    zmq_mock = setup_mocks(mocker, (b"Identity", STOP_TEST, b"Stop"), "return_value")
    test_runner_mock = mocker.patch(
        "bfgg.agent.message_handlers.incoming.GatlingRunner"
    )

    message_handler = IncomingMessageHandler(
        zmq_mock,
        controller_host,
        port,
        tests_location,
        results_folder,
        gatling_location,
    )
    message_handler._message_handler_loop()

    assert message_handler

    test_runner_mock.return_value.stop_runner.assert_not_called()
