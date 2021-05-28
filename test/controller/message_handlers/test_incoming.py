import pickle
from dataclasses import dataclass
from unittest import mock
from pytest import fixture

from zmq import Context

from bfgg.aws import S3Bucket
from bfgg.controller import State, DynamoTableInteractor
from bfgg.controller.message_handlers.incoming import IncomingMessageHandler
from bfgg.utils.messages import LOG, STATUS, BYE, START_TEST, FINISHED_TEST
from bfgg.utils.agentstatus import AgentStatus

port = 123
results_folder = "/results"
gatling_location = "/gatling"


@dataclass
class Mocks:
    metrics: mock.MagicMock
    context: mock.MagicMock
    state: mock.MagicMock
    dynamodb: mock.MagicMock
    s3_bucket: mock.MagicMock
    logger: mock.MagicMock
    report_handler: mock.MagicMock
    create_or_empty_folder: mock.MagicMock


class TestIncomingMessageHandler:
    @fixture
    def setup(self, mocker):
        metrics = mocker.patch(
            "bfgg.controller.message_handlers.incoming.MetricsHandler"
        )
        logger = mocker.patch("bfgg.controller.message_handlers.incoming.logger")
        report_handler = mocker.patch(
            "bfgg.controller.message_handlers.incoming.ReportHandler"
        )
        create_or_empty_folder = mocker.patch(
            "bfgg.controller.message_handlers.incoming.create_or_empty_results_folder"
        )
        context = mock.create_autospec(Context)
        state = mock.create_autospec(State)
        s3_bucket = mock.create_autospec(S3Bucket)
        dynamodb = mock.create_autospec(DynamoTableInteractor)
        incoming_message_handler = IncomingMessageHandler(
            context,
            port,
            results_folder,
            state,
            gatling_location,
            s3_bucket,
            dynamodb,
        )
        yield incoming_message_handler, Mocks(
            metrics,
            context,
            state,
            dynamodb,
            s3_bucket,
            logger,
            report_handler,
            create_or_empty_folder,
        )

    def test_controller_message_handler_loop_log(self, setup):
        incoming_message_handler, mocks = setup
        mocks.context.socket.return_value.recv_multipart.return_value = (
            b"Identity",
            b"group",
            LOG,
            b"Message",
        )

        incoming_message_handler._message_handler_loop()

        mocks.metrics.return_value.handle_log.assert_called_once_with(
            b"Identity", b"Message", b"group"
        )

    def test_controller_message_handler_loop_status(self, setup):
        incoming_message_handler, mocks = setup
        message = pickle.dumps(
            {
                "status": AgentStatus.TEST_STOPPED,
                "cloned_repos": {"a", "b"},
                "test_running": "Test",
                "extra_info": "interesting stuff",
            }
        )
        mocks.context.socket.return_value.recv_multipart.return_value = (
            b"Identity",
            b"group",
            STATUS,
            message,
        )

        incoming_message_handler._message_handler_loop()

        mocks.state.update_agent_state.assert_called_once_with(
            b"Identity", pickle.loads(message)
        )

    def test_controller_message_handler_loop_bye(self, setup):
        incoming_message_handler, mocks = setup
        mocks.context.socket.return_value.recv_multipart.return_value = (
            b"Identity",
            b"group",
            BYE,
            b"Bye",
        )

        incoming_message_handler._message_handler_loop()

        mocks.state.remove_agent.assert_called_once_with(b"Identity")

    def test_controller_message_handler_loop_start(self, setup):
        incoming_message_handler, mocks = setup
        mocks.context.socket.return_value.recv_multipart.return_value = (
            b"Identity",
            b"group",
            START_TEST,
            b"Start",
        )

        incoming_message_handler._message_handler_loop()

        mocks.create_or_empty_folder.assert_called_once_with(results_folder, "group")

    def test_controller_message_handler_loop_finished_all_agents(self, setup, mocker):
        incoming_message_handler, mocks = setup
        mocks.context.socket.return_value.recv_multipart.return_value = (
            b"Identity",
            b"group",
            FINISHED_TEST,
            b"1234",
        )
        mocks.state.all_agents_finished_in_group.return_value = True
        mocks.report_handler.return_value.run.return_value = "results.url"
        datetime_mock = mocker.patch(
            "bfgg.controller.message_handlers.incoming.datetime"
        )
        datetime_mock.utcnow.return_value = "datetime.utcnow"

        incoming_message_handler._message_handler_loop()

        mocks.logger.info.assert_has_calls(
            [
                mocker.call("Identity finished test"),
                mocker.call("Generating report for group group"),
            ]
        )
        mocks.state.update_agent_status.assert_called_once_with(
            b"Identity", AgentStatus.TEST_FINISHED
        )
        mocks.report_handler.assert_called_once_with(
            results_folder, gatling_location, mocks.s3_bucket, "group"
        )
        mocks.report_handler.return_value.run.assert_called_once()
        mocks.dynamodb.update_test_ended.assert_called_with(
            "1234", "datetime.utcnow", "results.url"
        )

    def test_controller_message_handler_loop_finished_not_all_agents(
        self, setup, mocker
    ):
        incoming_message_handler, mocks = setup
        mocks.context.socket.return_value.recv_multipart.return_value = (
            b"Identity",
            b"group",
            FINISHED_TEST,
            b"Finish",
        )

        mocks.state.all_agents_finished_in_group.return_value = False
        report_handler_mock = mocker.patch(
            "bfgg.controller.message_handlers.incoming.ReportHandler"
        )

        incoming_message_handler._message_handler_loop()

        mocks.logger.info.assert_called_once_with("Identity finished test")
        mocks.state.update_agent_status.assert_called_once_with(
            b"Identity", AgentStatus.TEST_FINISHED
        )
        report_handler_mock.assert_not_called()
