import pickle

from bfgg.controller.message_handlers.incoming import IncomingMessageHandler
from bfgg.utils.messages import LOG, STATUS, BYE, START_TEST, FINISHED_TEST
from bfgg.utils.agentstatus import AgentStatus

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
    state_mock, zmq_mock, metrics_mock = setup_mocks(mocker, (b'Identity', b'group', LOG, b'Message'))

    message_handler = IncomingMessageHandler(zmq_mock, port, results_folder, state_mock,
                                             gatling_location, s3_bucket, s3_region)
    message_handler._message_handler_loop()

    metrics_mock.return_value.handle_log.assert_called_once_with(b'Identity', b'Message', b'group')


def test_controller_message_handler_loop_status(mocker):
    message = pickle.dumps(
        {
            'status': AgentStatus.TEST_STOPPED,
            'cloned_repos': {'a', 'b'},
            'test_running': 'Test',
            'extra_info': 'interesting stuff'
        }
    )
    state_mock, zmq_mock, _ = setup_mocks(mocker, (b'Identity', b'group', STATUS, message))

    message_handler = IncomingMessageHandler(zmq_mock, port, results_folder, state_mock,
                                             gatling_location, s3_bucket, s3_region)
    message_handler._message_handler_loop()

    state_mock.update_agent_state.assert_called_once_with(b'Identity', pickle.loads(message))


def test_controller_message_handler_loop_bye(mocker):
    state_mock, zmq_mock, _ = setup_mocks(mocker, (b'Identity', b'group', BYE, b'Bye'))

    message_handler = IncomingMessageHandler(zmq_mock, port, results_folder, state_mock,
                                             gatling_location, s3_bucket, s3_region)
    message_handler._message_handler_loop()

    state_mock.remove_agent.assert_called_once_with(b'Identity')


def test_controller_message_handler_loop_start(mocker):
    state_mock, zmq_mock, _ = setup_mocks(mocker, (b'Identity', b'group', START_TEST, b'Start'))
    create_or_empty_folder_mock = mocker.patch('bfgg.controller.message_handlers.incoming.create_or_empty_results_folder')

    message_handler = IncomingMessageHandler(zmq_mock, port, results_folder, state_mock,
                                             gatling_location, s3_bucket, s3_region)
    message_handler._message_handler_loop()

    create_or_empty_folder_mock.assert_called_once_with(results_folder, 'group')


def test_controller_message_handler_loop_finished_all_agents(mocker):
    state_mock, zmq_mock, _ = setup_mocks(mocker, (b'Identity', b'group', FINISHED_TEST, b'1234'))
    state_mock.all_agents_finished_in_group.return_value = True
    logging_mock = mocker.patch('bfgg.controller.message_handlers.incoming.logger')
    report_handler_mock = mocker.patch('bfgg.controller.message_handlers.incoming.ReportHandler')
    report_handler_mock.return_value.run.return_value = "results.url"
    dynamodb_mock = mocker.patch('bfgg.controller.message_handlers.incoming.DYNAMO_DB')
    datetime_mock = mocker.patch('bfgg.controller.message_handlers.incoming.datetime')
    datetime_mock.utcnow.return_value = "datetime.utcnow"

    message_handler = IncomingMessageHandler(zmq_mock, port, results_folder, state_mock,
                                             gatling_location, s3_bucket, s3_region)
    message_handler._message_handler_loop()

    logging_mock.info.assert_has_calls([
        mocker.call('Identity finished test'),
        mocker.call('Generating report for group group')
    ])
    state_mock.update_agent_status.assert_called_once_with(b'Identity', AgentStatus.TEST_FINISHED)
    report_handler_mock.assert_called_once_with(results_folder, gatling_location, s3_bucket, s3_region, 'group')
    report_handler_mock.return_value.run.assert_called_once()
    dynamodb_mock.update_test_ended.assert_called_with("1234", "datetime.utcnow", "results.url")


def test_controller_message_handler_loop_finished_not_all_agents(mocker):
    state_mock, zmq_mock, _ = setup_mocks(mocker, (b'Identity', b'group', FINISHED_TEST, b'Finish'))
    state_mock.all_agents_finished_in_group.return_value = False
    logging_mock = mocker.patch('bfgg.controller.message_handlers.incoming.logger')
    report_handler_mock = mocker.patch('bfgg.controller.message_handlers.incoming.ReportHandler')

    message_handler = IncomingMessageHandler(zmq_mock, port, results_folder, state_mock,
                                             gatling_location, s3_bucket, s3_region)
    message_handler._message_handler_loop()

    logging_mock.info.assert_called_once_with('Identity finished test')
    state_mock.update_agent_status.assert_called_once_with(b'Identity', AgentStatus.TEST_FINISHED)
    report_handler_mock.assert_not_called()
