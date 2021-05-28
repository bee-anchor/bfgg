from dataclasses import dataclass
from queue import Queue
from unittest import mock

from pytest import fixture
from zmq import Context

from bfgg.agent import AgentUtils
from bfgg.agent.message_handlers.incoming import IncomingMessageHandler
from bfgg.utils.messages import CLONE, START_TEST, STOP_TEST

controller_host = "localhost"
port = "8080"
tests_location = "/tests"
results_folder = "/results"
gatling_location = "/gatling"


@dataclass
class Mocks:
    agent_utils: mock.MagicMock
    context: mock.MagicMock
    outgoing_queue: mock.MagicMock


class TestIncomingMessageHandler:
    @fixture
    def setup(self):
        agent_utils = mock.create_autospec(AgentUtils)
        context = mock.create_autospec(Context)
        outgoing_queue = mock.create_autospec(Queue)
        inc_mess_handler = IncomingMessageHandler(
            "test",
            agent_utils,
            context,
            controller_host,
            port,
            tests_location,
            results_folder,
            gatling_location,
            outgoing_queue,
            0.1,
        )
        return inc_mess_handler, Mocks(agent_utils, context, outgoing_queue)

    def test_clone(self, setup, mocker):
        incoming_message_handler, mocks = setup
        mocks.context.socket.return_value.recv_multipart.return_value = (
            b"Identity",
            CLONE,
            b"Message",
        )
        clone_mock = mocker.patch("bfgg.agent.message_handlers.incoming.clone_repo")

        incoming_message_handler._message_handler_loop()

        mocks.context.socket.return_value.recv_multipart.assert_called_once()
        clone_mock.assert_called_once()
        clone_mock.assert_called_with("Message", tests_location, mocks.agent_utils)

    def test_start_test(self, setup, mocker):
        incoming_message_handler, mocks = setup
        mocks.context.socket.return_value.recv_multipart.return_value = (
            b"Identity",
            START_TEST,
            b"1234,Project,Test,Java opts",
        )
        test_runner_mock = mocker.patch(
            "bfgg.agent.message_handlers.incoming.GatlingRunner"
        )

        incoming_message_handler._message_handler_loop()

        mocks.context.socket.return_value.recv_multipart.assert_called_once()
        test_runner_mock.assert_called_once()
        test_runner_mock.assert_called_with(
            gatling_location,
            tests_location,
            results_folder,
            "1234",
            "Project",
            "Test",
            "Java opts",
            mocks.outgoing_queue,
            0.1,
            mocks.agent_utils,
        )
        test_runner_mock.return_value.start.assert_called_once()

    def test_stop_test_runner_exists(self, setup, mocker):
        incoming_message_handler, mocks = setup
        mocks.context.socket.return_value.recv_multipart.side_effect = [
            (b"Identity", START_TEST, b"1234,Project,Test,Java opts"),
            (b"Identity", STOP_TEST, b"Stop"),
        ]
        test_runner_mock = mocker.patch(
            "bfgg.agent.message_handlers.incoming.GatlingRunner"
        )

        incoming_message_handler._message_handler_loop()
        incoming_message_handler._message_handler_loop()

        assert mocks.context.socket.return_value.recv_multipart.call_count == 2
        assert test_runner_mock.return_value.stop_runner is True

    def test_stop_test_runner_doesnt_exist(self, setup, mocker):
        incoming_message_handler, mocks = setup
        mocks.context.socket.return_value.recv_multipart.return_value = (
            b"Identity",
            STOP_TEST,
            b"Stop",
        )
        test_runner_mock = mocker.patch(
            "bfgg.agent.message_handlers.incoming.GatlingRunner"
        )

        incoming_message_handler._message_handler_loop()

        test_runner_mock.return_value.stop_runner.assert_not_called()
