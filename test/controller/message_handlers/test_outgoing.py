from queue import Empty

from bfgg.controller.message_handlers.outgoing import OutgoingMessageHandler


def setup_mocks(mocker):
    zmq_mock = mocker.patch('bfgg.controller.message_handlers.outgoing.zmq')
    state_mock = mocker.patch('bfgg.controller.message_handlers.outgoing.State')
    type(state_mock).connected_agents = mocker.PropertyMock(return_value=['A', 'B'])

    return zmq_mock, state_mock

def test_message_handler_loop(mocker):

    zmq_mock, state_mock = setup_mocks(mocker)
    type(state_mock).connected_agents = mocker.PropertyMock(return_value=['A', 'B'])
    outgoing_queue_mock = mocker.MagicMock(**{
        'get.return_value.type': b'TYPE',
        'get.return_value.details': b'DETAILS'
    })

    message_handler = OutgoingMessageHandler(zmq_mock, 'port', state_mock, outgoing_queue_mock)
    message_handler._message_handler_loop()

    assert 2 == zmq_mock.socket.return_value.send_multipart.call_count
    zmq_mock.socket.return_value.send_multipart.assert_called_with([b'controller', b'TYPE', b'DETAILS'])

def test_message_handler_loop_no_message(mocker):

    zmq_mock, state_mock = setup_mocks(mocker)
    outgoing_queue_mock = mocker.MagicMock(**{
        'get.side_effect': Empty
    })

    message_handler = OutgoingMessageHandler(zmq_mock, 'port', state_mock, outgoing_queue_mock)
    message_handler._message_handler_loop()

    assert 0 == zmq_mock.socket.return_value.send_multipart.call_count