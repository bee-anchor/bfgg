from pytest import fixture
from unittest.mock import call
from queue import Queue
from bfgg.utils.messages import OutgoingMessageGrouped

from bfgg.controller.message_handlers.outgoing import OutgoingMessageHandler


class TestOutgoingMessageHandler:
    @fixture()
    def mocks(self, mocker):
        zmq_mock = mocker.patch("bfgg.controller.message_handlers.outgoing.zmq")
        state_mock = mocker.patch("bfgg.controller.message_handlers.outgoing.State")
        state_mock.configure_mock(
            **{"connected_agents_by_group.return_value": [b"A", b"B"]}
        )
        outgoing_queue = Queue()

        yield zmq_mock, state_mock, outgoing_queue

    def test_message_handler_loop(self, mocks):
        zmq_mock, state_mock, outgoing_queue = mocks

        message_handler = OutgoingMessageHandler(
            zmq_mock, "port", state_mock, outgoing_queue
        )
        outgoing_queue.put(OutgoingMessageGrouped(b"TYPE", b"DETAILS", b"GROUP"))
        message_handler._message_handler_loop()

        assert zmq_mock.socket.return_value.send_multipart.call_count == 2
        zmq_mock.socket.return_value.send_multipart.assert_has_calls(
            [
                call([b"A", b"controller", b"TYPE", b"DETAILS"]),
                call([b"B", b"controller", b"TYPE", b"DETAILS"]),
            ]
        )

    def test_message_handler_loop_no_message(self, mocks):
        zmq_mock, state_mock, outgoing_queue = mocks

        message_handler = OutgoingMessageHandler(
            zmq_mock, "port", state_mock, outgoing_queue
        )
        message_handler._message_handler_loop()
        zmq_mock.socket.return_value.send_multipart.assert_not_called()
