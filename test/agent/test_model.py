from bfgg.agent.model import get_identity


def test_get_identity(mocker):
    socket_mock = mocker.patch('socket.socket', **{
        'return_value.getsockname.return_value': ['99.99.99.99', '88.88.88.88']
    })
    identity = "identity"
    result = get_identity(identity)
    socket_mock.return_value.connect.assert_called_with((identity, 80))
    socket_mock.return_value.getsockname.assert_called_once()
    assert '99.99.99.99' == result
