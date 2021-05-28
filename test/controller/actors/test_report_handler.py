from unittest import mock
from unittest.mock import call

from pytest import fixture

from bfgg.controller.actors.report_handler import ReportHandler
from bfgg.aws import S3Bucket


class TestReportHandler:
    results_folder = "a/b/c"
    group = "ungrouped"
    group_results_folder = f"a/b/c/{group}"
    gatling_folder = "d/e/f"
    bucket = "my_bucket"

    @fixture
    def setup(self):
        s3_bucket = mock.create_autospec(S3Bucket)
        s3_bucket.bucket_name = "my_bucket"
        report_handler = ReportHandler(
            self.results_folder, self.gatling_folder, s3_bucket, self.group
        )
        return report_handler, s3_bucket

    def test_content_type_from_file(self, setup):
        report_handler, _ = setup
        assert (
            report_handler._content_type_from_file("some_file.js")
            == "application/javascript"
        )

    def test_generate_report(self, setup, mocker):
        report_handler, _ = setup
        subprocess_mock = mocker.patch(
            "bfgg.controller.actors.report_handler.subprocess",
            **{"Popen.return_value.communicate.return_value": (b"Stdout", b"Stderr")},
        )
        logging_mock = mocker.MagicMock()
        report_handler.logger = logging_mock

        report_handler._generate_report()
        assert [
            f"{self.gatling_folder}/bin/gatling.sh",
            "-ro",
            self.group_results_folder,
        ] in subprocess_mock.Popen.call_args[0]
        logging_mock.info.assert_has_calls(
            [
                mocker.call(
                    [
                        f"{self.gatling_folder}/bin/gatling.sh",
                        "-ro",
                        self.group_results_folder,
                    ]
                ),
                mocker.call("Stdout"),
            ]
        )

    def test_upload_results(self, setup, mocker):
        report_handler, s3_mock = setup
        mocker.patch(
            "bfgg.controller.actors.report_handler.datetime",
            **{"now.return_value.strftime.return_value": "NOW"},
        )
        mocker.patch(
            "bfgg.controller.actors.report_handler.os.walk",
            **{
                "side_effect": [
                    [
                        (self.group_results_folder, ["2", "3"], ["1.html"]),
                        (self.group_results_folder + "/2", [], ["2.png"]),
                        (self.group_results_folder + "/3", [], ["3.json"]),
                    ]
                ]
            },
        )
        mocker.patch("bfgg.controller.actors.report_handler.shutil")
        logging_mock = mocker.patch("bfgg.controller.actors.report_handler.logger")

        assert (
            report_handler._upload_results()
            == f"https://{self.bucket}.s3.amazonaws.com/NOW/index.html"
        )
        logging_mock.info.asser_called_with(
            f"https://{self.bucket}.s3.amazonaws.com/NOW/index.html"
        )

        s3_mock.upload_file.assert_has_calls(
            [
                call(
                    "NOW/1.html",
                    "a/b/c/ungrouped/1.html",
                    extra_args={"ACL": "private", "ContentType": "text/html"},
                ),
                call(
                    "NOW/2/2.png",
                    "a/b/c/ungrouped/2/2.png",
                    extra_args={"ACL": "private", "ContentType": "image/png"},
                ),
                call(
                    "NOW/3/3.json",
                    "a/b/c/ungrouped/3/3.json",
                    extra_args={"ACL": "private", "ContentType": "application/json"},
                ),
            ]
        )
