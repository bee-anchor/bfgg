import pickle

from bfgg.controller.message_handlers.incoming import IncomingMessageHandler
from bfgg.utils.messages import LOG, STATUS, BYE, START_TEST, FINISHED_TEST
from bfgg.utils.statuses import Statuses

port = 'port'
results_folder = '/results'
gatling_location = '/gatling'
s3_bucket = 'bucket'
s3_region = 'region'


def setup_mocks(mocker, return_value):
    state_mock = mocker.patch('bfgg.controller.message_handlers.incoming.State')
    zmq_mock = mocker.patch('bfgg.controller.message_handlers.incoming.zmq', **{
        f'socket.return_value.recv_multipart.return_value': return_value
    })
    metrics_mock = mocker.patch('bfgg.controller.message_handlers.incoming.MetricsHandler')

    return state_mock, zmq_mock, metrics_mock


def test_controller_message_handler_loop_log(mocker):
    state_mock, zmq_mock, metrics_mock = setup_mocks(mocker, (b'Identity', LOG, b'Message'))

    message_handler = IncomingMessageHandler(zmq_mock, port, results_folder, state_mock,
                                             gatling_location, s3_bucket, s3_region)
    message_handler._message_handler_loop()

    metrics_mock.return_value.handle_log.assert_called_once_with(b'Identity', b'Message')


def test_controller_message_handler_loop_status(mocker):
    message = pickle.dumps(
        {
            'status': Statuses.TEST_STOPPED,
            'cloned_repos': {'a', 'b'},
            'test_running': 'Test',
            'extra_info': 'interesting stuff'
        }
    )
    state_mock, zmq_mock, _ = setup_mocks(mocker, (b'Identity', STATUS, message))

    message_handler = IncomingMessageHandler(zmq_mock, port, results_folder, state_mock,
                                             gatling_location, s3_bucket, s3_region)
    message_handler._message_handler_loop()

    state_mock.update_agent.assert_called_once_with(b'Identity', pickle.loads(message))


def test_controller_message_handler_loop_bye(mocker):
    state_mock, zmq_mock, _ = setup_mocks(mocker, (b'Identity', BYE, b'Bye'))

    message_handler = IncomingMessageHandler(zmq_mock, port, results_folder, state_mock,
                                             gatling_location, s3_bucket, s3_region)
    message_handler._message_handler_loop()

    state_mock.remove_agent.assert_called_once_with(b'Identity')


def test_controller_message_handler_loop_start(mocker):
    state_mock, zmq_mock, _ = setup_mocks(mocker, (b'Identity', START_TEST, b'Start'))
    create_or_empty_folder_mock = mocker.patch('bfgg.controller.message_handlers.incoming.create_or_empty_folder')

    message_handler = IncomingMessageHandler(zmq_mock, port, results_folder, state_mock,
                                             gatling_location, s3_bucket, s3_region)
    message_handler._message_handler_loop()

    create_or_empty_folder_mock.assert_called_once_with(results_folder)


def test_controller_message_handler_loop_finished_all_agents(mocker):
    state_mock, zmq_mock, _ = setup_mocks(mocker, (b'Identity', FINISHED_TEST, b'Finish'))
    state_mock.all_agents_finished.return_value = True
    report_handler_mock = mocker.patch('bfgg.controller.message_handlers.incoming.ReportHandler')

    message_handler = IncomingMessageHandler(zmq_mock, port, results_folder, state_mock,
                                             gatling_location, s3_bucket, s3_region)
    message_handler._message_handler_loop()

    state_mock.update_agent.assert_called_once_with(b'Identity', )
    report_handler_mock.assert_called_once_with(results_folder, gatling_location, s3_bucket, s3_region)
    report_handler_mock.return_value.run.assert_called_once()

def test_controller_message_handler_loop_finished_not_all_agents(mocker):
    state_mock, zmq_mock, _ = setup_mocks(mocker, (b'Identity', FINISHED_TEST, b'Finish'))
    state_mock.all_agents_finished.return_value = False
    report_handler_mock = mocker.patch('bfgg.controller.message_handlers.incoming.ReportHandler')

    message_handler = IncomingMessageHandler(zmq_mock, port, results_folder, state_mock,
                                             gatling_location, s3_bucket, s3_region)
    message_handler._message_handler_loop()

    state_mock.update_agent.assert_called_once_with(b'Identity', )
    report_handler_mock.assert_not_called()