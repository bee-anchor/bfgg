from bfgg.agent.message_handlers.outgoing import OutgoingMessageHandler
from bfgg.utils.messages import BYE


def setup_mocks(mocker):
    zmq_mock = mocker.patch("bfgg.agent.message_handlers.outgoing.zmq")
    return zmq_mock


def test_agent_outgoing_message_handler_loop(mocker):
    outgoing_queue_mock = mocker.patch(
        "bfgg.agent.message_handlers.outgoing.OUTGOING_QUEUE",
        **{"get.return_value.type": b"TYPE", "get.return_value.details": b"DETAILS"}
    )
    zmq_mock = setup_mocks(mocker)
    OutgoingMessageHandler(
        zmq_mock, "localhost", "8080", b"localhost"
    )._message_handler_loop()
    outgoing_queue_mock.get.assert_called_once()
    zmq_mock.socket.return_value.send_multipart.assert_called_once_with(
        [b"localhost", b"ungrouped", b"TYPE", b"DETAILS"]
    )


def test_agent_outgoing_message_handler_exit(mocker):
    zmq_mock = setup_mocks(mocker)
    OutgoingMessageHandler(
        zmq_mock, "localhost", "8080", b"localhost"
    ).exit_gracefully()
    zmq_mock.socket.return_value.send_multipart.assert_called_once_with(
        [b"localhost", b"ungrouped", BYE, b"goodbye"]
    )
