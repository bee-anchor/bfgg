import logging.config
import os
import subprocess
from datetime import datetime
import boto3


class ReportHandler():

    def __init__(self, results_folder: str, gatling_location, s3_bucket: str, s3_region: str):
        self.results_folder = results_folder
        self.gatling_location = gatling_location
        self.s3_bucket = s3_bucket
        self.s3_region = s3_region

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
            "svg": "image/svg+xml"
        }

        type = filename.split('.')[-1]
        return content_types[type]

    def _generate_report(self):
        logging.info([f'{self.gatling_location}/bin/gatling.sh', '-ro', self.results_folder])
        report_process = subprocess.Popen(
            [f'{self.gatling_location}/bin/gatling.sh', '-ro', self.results_folder],
            cwd=self.results_folder,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        stdout, stderror = report_process.communicate()
        stdout = stdout.decode('utf-8')
        logging.info(stdout)

    def _upload_results(self):

        folder = datetime.now().strftime("%Y%m%d_%H%M")
        s3 = boto3.resource('s3', region_name=self.s3_region)

        for file in os.listdir(self.results_folder):
            path = os.path.join(self.results_folder, file)
            if os.path.isfile(path):
                with open(path, "rb") as opened_file:
                    s3.Bucket(self.s3_bucket).put_object(Key=f"{folder}/{file}", Body=opened_file.read(), ACL='private',
                                                         ContentType=self._content_type_from_file(file))
            elif os.path.isdir(path):
                # report created only has one level of nesting
                for sub_file in os.listdir(os.path.join(self.results_folder, file)):
                    with open(os.path.join(path, sub_file), "rb") as opened_file:
                        s3.Bucket(self.s3_bucket).put_object(Key=f"{folder}/{file}/{sub_file}", Body=opened_file.read(),
                                                             ACL='private',
                                                             ContentType=self._content_type_from_file(sub_file))

        url = f'https://{self.s3_bucket}.s3.amazonaws.com/{folder}/index.html'
        return url

    def run(self):
        self._generate_report()
        url = self._upload_results()
        return url
