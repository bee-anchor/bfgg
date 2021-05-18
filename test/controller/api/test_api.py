from pytest import fixture
import json
from bfgg.controller import create_app
from bfgg.utils.messages import OutgoingMessageGrouped, CLONE, START_TEST, STOP_TEST


class TestApi:
    app = create_app()
    app.testing = True
    client = app.test_client

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
    def mocks(self, mocker):
        outgoing_queue_mock = mocker.patch("bfgg.controller.api.OUTGOING_QUEUE")
        return outgoing_queue_mock

    def test_clone_bad_request(self):
        res = self.client().post(
            "/clone",
            content_type="'application/json'",
            data=json.dumps(self.bad_clone_data),
        )
        assert res.status_code == 400

    def test_clone(self, mocks):
        outgoing_queue_mock = mocks
        res = self.client().post(
            "/clone",
            content_type="'application/json'",
            data=json.dumps(self.clone_data),
        )
        assert res.status_code == 200
        outgoing_queue_mock.put.assert_called_with(
            OutgoingMessageGrouped(CLONE, self.repo.encode("utf-8"), b"ungrouped")
        )

    def test_start_bad_request(self):
        res = self.client().post(
            "/start",
            content_type="'application/json'",
            data=json.dumps(self.bad_start_data),
        )
        assert res.status_code == 400

    def test_start(self, mocks, mocker):
        outgoing_queue_mock = mocks
        create_folder_mock = mocker.patch(
            "bfgg.controller.api.create_or_empty_results_folder"
        )
        dynamodb_mock = mocker.patch("bfgg.controller.api.DYNAMO_DB")
        datetime_mock = mocker.patch("bfgg.controller.api.datetime")
        uuid_mock = mocker.patch("bfgg.controller.api.uuid4")
        uuid_mock.return_value = "1234"
        datetime_mock.utcnow.return_value = "datetime_now"

        res = self.client().post(
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
        outgoing_queue_mock.put.assert_called_with(
            OutgoingMessageGrouped(START_TEST, expected_task, b"ungrouped")
        )
        dynamodb_mock.save_test_started.assert_called_with(
            "1234",
            "datetime_now",
            self.start_data["project"],
            self.start_data["testClass"],
            self.start_data["javaOpts"],
        )

    def test_stop_bad_request(self):
        res = self.client().post(
            "/stop",
            content_type="'application/json'",
            data=json.dumps(self.bad_stop_data),
        )
        assert res.status_code == 400

    def test_stop(self, mocks):
        outgoing_queue_mock = mocks
        res = self.client().post(
            "/stop", content_type="'application/json'", data=json.dumps(self.stop_data)
        )
        assert res.status_code == 200
        outgoing_queue_mock.put.assert_called_with(
            OutgoingMessageGrouped(STOP_TEST, b"STOP", b"ungrouped")
        )

    def test_status(self, mocker):
        mocker.patch(
            "bfgg.controller.api.STATE",
            **{
                "current_agents_state_list.return_value": [
                    {
                        "identity": "A",
                        "status": "AVAILABLE",
                        "cloned_repos": [],
                        "test_running": "",
                        "extra_info": "",
                    }
                ]
            },
        )
        res = self.client().get("/status")
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

    def test_results_bad_request(self):
        res = self.client().post(
            "/results",
            content_type="'application/json'",
            data=json.dumps(self.bad_results_data),
        )
        assert res.status_code == 400

    def test_results(self, mocker):
        mocker.patch(
            "bfgg.controller.api.ReportHandler",
            **{"return_value.run.return_value": "http://www.example.com"},
        )
        res = self.client().post(
            "/results",
            content_type="'application/json'",
            data=json.dumps(self.results_data),
        )
        assert res.status_code == 200
        assert "http://www.example.com" in next(res.response).decode("utf-8")
