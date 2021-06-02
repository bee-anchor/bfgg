import json
from dataclasses import dataclass
from queue import Queue
from unittest import mock

from pytest import fixture

from bfgg.controller.actors.dynamodb_resource import DynamoTableInteractor
from bfgg.controller.state import State
from bfgg.controller.__init__ import create_app
from bfgg.utils.messages import CLONE, START_TEST, STOP_TEST, OutgoingMessageGrouped


@dataclass()
class Mocks:
    config: mock.MagicMock
    state: mock.MagicMock
    outgoing_queue: mock.MagicMock
    dynamodb: mock.MagicMock


class TestApi:
    repo = "git@bitbucket.org:blah/bleh.git"
    bad_clone_data = {"repo": repo}
    clone_data = {"repo": repo, "group": "ungrouped"}
    bad_start_data = {
        "perject": repo,
        "testClass": "FullTest",
        "javaOpts": "-Xmx14G -DCONFIG1=500 -DCONFIG2=999999",
        "group": "ungrouped",
    }
    start_data = {
        "project": repo,
        "testClass": "FullTest",
        "javaOpts": "-Xmx14G -DCONFIG1=500 -DCONFIG2=999999",
        "group": "ungrouped",
    }
    bad_stop_data = {"gerp": "ungrouped"}
    stop_data = {"group": "ungrouped"}
    bad_results_data = {"gerp": "ungrouped"}
    results_data = {"group": "ungrouped"}

    @fixture()
    def setup(self):
        config = mock.MagicMock()
        state = mock.MagicMock(spec=State)
        outgoing_queue = mock.MagicMock(spec=Queue)
        dynamodb = mock.MagicMock(spec=DynamoTableInteractor)
        app = create_app(config, state, outgoing_queue, dynamodb)
        app.testing = True
        client = app.test_client
        return client, Mocks(config, state, outgoing_queue, dynamodb)

    def test_clone_bad_request(self, setup):
        client, _ = setup
        res = client().post(
            "/clone",
            content_type="'application/json'",
            data=json.dumps(self.bad_clone_data),
        )
        assert res.status_code == 400

    def test_clone(self, setup):
        client, mocks = setup
        res = client().post(
            "/clone",
            content_type="'application/json'",
            data=json.dumps(self.clone_data),
        )
        assert res.status_code == 200
        mocks.outgoing_queue.put.assert_called_with(
            OutgoingMessageGrouped(CLONE, self.repo.encode("utf-8"), b"ungrouped")
        )

    def test_start_bad_request(self, setup):
        client, _ = setup
        res = client().post(
            "/start",
            content_type="'application/json'",
            data=json.dumps(self.bad_start_data),
        )
        assert res.status_code == 400

    def test_start(self, setup, mocker):
        client, mocks = setup
        mocks.config.results_folder = "blah"
        create_folder_mock = mocker.patch(
            "bfgg.controller.api.create_or_empty_results_folder"
        )
        datetime_mock = mocker.patch("bfgg.controller.api.datetime")
        uuid_mock = mocker.patch("bfgg.controller.api.uuid4")
        uuid_mock.return_value = "1234"
        datetime_mock.utcnow.return_value = "datetime_now"

        res = client().post(
            "/start",
            content_type="'application/json'",
            data=json.dumps(self.start_data),
        )
        assert res.status_code == 200
        create_folder_mock.assert_called_once()
        expected_task = (
            f"1234,{self.start_data['project']},"
            f"{self.start_data['testClass']},"
            f"{self.start_data['javaOpts']}"
        ).encode("utf-8")
        mocks.outgoing_queue.put.assert_called_with(
            OutgoingMessageGrouped(START_TEST, expected_task, b"ungrouped")
        )
        mocks.dynamodb.save_test_started.assert_called_with(
            "1234",
            "datetime_now",
            self.start_data["project"],
            self.start_data["testClass"],
            self.start_data["javaOpts"],
        )

    def test_stop_bad_request(self, setup):
        client, _ = setup
        res = client().post(
            "/stop",
            content_type="'application/json'",
            data=json.dumps(self.bad_stop_data),
        )
        assert res.status_code == 400

    def test_stop(self, setup):
        client, mocks = setup
        res = client().post(
            "/stop", content_type="'application/json'", data=json.dumps(self.stop_data)
        )
        assert res.status_code == 200
        mocks.outgoing_queue.put.assert_called_with(
            OutgoingMessageGrouped(STOP_TEST, b"STOP", b"ungrouped")
        )

    def test_status(self, setup):
        client, mocks = setup
        mocks.state.current_agents_state_list.return_value = [
            {
                "identity": "A",
                "status": "AVAILABLE",
                "cloned_repos": [],
                "test_running": "",
                "extra_info": "",
            }
        ]
        res = client().get("/status")
        expected = [
            {
                "identity": "A",
                "status": "AVAILABLE",
                "cloned_repos": [],
                "test_running": "",
                "extra_info": "",
            }
        ]
        assert res.status_code == 200
        assert res.json == expected

    def test_results_bad_request(self, setup):
        client, _ = setup
        res = client().post(
            "/results",
            content_type="'application/json'",
            data=json.dumps(self.bad_results_data),
        )
        assert res.status_code == 400

    def test_results(self, setup, mocker):
        client, _ = setup
        mocker.patch(
            "bfgg.controller.api.ReportHandler",
            **{"return_value.run.return_value": "http://www.example.com"},
        )
        res = client().post(
            "/results",
            content_type="'application/json'",
            data=json.dumps(self.results_data),
        )
        assert res.status_code == 200
        assert "http://www.example.com" in next(res.response).decode("utf-8")
