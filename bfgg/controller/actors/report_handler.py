import os
import shutil
import subprocess
from datetime import datetime
from bfgg.utils.logging import logger
from bfgg.aws import S3Bucket


class ReportHandler:
    def __init__(
        self,
        results_folder: str,
        gatling_location,
        s3_bucket: S3Bucket,
        group: str,
    ):
        self.logger = logger
        self.results_folder = os.path.join(results_folder, group)
        self.gatling_location = gatling_location
        self.s3_bucket = s3_bucket

    @staticmethod
    def _content_type_from_file(filename: str):
        content_types = {
            "html": "text/html",
            "png": "image/png",
            "css": "text/css",
            "jpg": "image/jpeg",
            "js": "application/javascript",
            "json": "application/json",
            "xml": "application/xml",
            "ico": "image/x-icon",
            "log": "text/plain",
            "svg": "image/svg+xml",
            "offset": "text/plain",
        }

        type = filename.split(".")[-1]
        return content_types[type]

    def _generate_report(self):
        self.logger.info(
            [f"{self.gatling_location}/bin/gatling.sh", "-ro", self.results_folder]
        )
        try:
            report_process = subprocess.Popen(
                [f"{self.gatling_location}/bin/gatling.sh", "-ro", self.results_folder],
                cwd=self.results_folder,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            stdout, stderror = report_process.communicate()
            stdout = stdout.decode("utf-8")
            self.logger.info(stdout)
        except Exception as e:
            self.logger.error(e)

    def _upload_results(self):
        folder = datetime.now().strftime("%Y%m%d_%H%M")
        try:
            for path, _, files in os.walk(self.results_folder):
                for file in files:
                    # if we're in the top directory
                    current_folder = os.path.basename(path)
                    if current_folder == os.path.basename(self.results_folder):
                        filename = f"{folder}/{file}"
                    else:
                        filename = f"{folder}/{current_folder}/{file}"
                    extra_args = {
                        "ACL": "private",
                        "ContentType": self._content_type_from_file(file),
                    }
                    self.s3_bucket.upload_file(
                        filename, os.path.join(path, file), extra_args=extra_args
                    )
            url = f"https://{self.s3_bucket.bucket_name}.s3.amazonaws.com/{folder}/index.html"
            self.logger.info(url)
            shutil.rmtree(self.results_folder)
            return url
        except Exception as e:
            self.logger.error(e)

    def run(self):
        self._generate_report()
        url = self._upload_results()
        return url
