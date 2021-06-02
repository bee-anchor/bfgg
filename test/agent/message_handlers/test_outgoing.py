from dataclasses import dataclass
from queue import Queue
from unittest import mock

from pytest import fixture
from zmq import Context


from bfgg.agent.state import State
from bfgg.agent.message_handlers.outgoing import OutgoingMessageHandler
from bfgg.utils.messages import BYE


@dataclass
class Mocks:
    context: mock.MagicMock
    state: mock.MagicMock
    outgoing_queue: mock.MagicMock


@fixture
def setup():
    context = mock.create_autospec(Context)
    state = mock.create_autospec(State)
    outgoing_queue = mock.create_autospec(Queue)
    outgoing_mess_handler = OutgoingMessageHandler(
        context, state, outgoing_queue, "localhost", "8080", b"localhost"
    )
    return outgoing_mess_handler, Mocks(context, state, outgoing_queue)


def test_agent_outgoing_message_handler_loop(setup):
    outgoing_messsage_handler, mocks = setup
    mocks.outgoing_queue.get.return_value.type = b"TYPE"
    mocks.outgoing_queue.get.return_value.details = b"DETAILS"
    mocks.state.group = "ungrouped"

    outgoing_messsage_handler._message_handler_loop()
    mocks.outgoing_queue.get.assert_called_once()
    mocks.context.socket.return_value.send_multipart.assert_called_once_with(
        [b"localhost", b"ungrouped", b"TYPE", b"DETAILS"]
    )


def test_agent_outgoing_message_handler_exit(setup):
    outgoing_messsage_handler, mocks = setup
    mocks.state.group = "ungrouped"
    outgoing_messsage_handler.exit_gracefully()
    mocks.context.socket.return_value.send_multipart.assert_called_once_with(
        [b"localhost", b"ungrouped", BYE, b"goodbye"]
    )
