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
            "svg": "image/svg+xml",
            "offset": "text/plain"
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
        for path,_,files in os.walk(self.results_folder):
            for file in files:
                # if we're in the top directory
                current_folder = os.path.basename(path)
                if current_folder == os.path.basename(self.results_folder):
                    filename = f'{folder}/{file}'
                else:
                    filename = f'{folder}/{current_folder}/{file}'
                extra_args = {'ACL': 'private', 'ContentType': self._content_type_from_file(file)}
                s3.Object(self.s3_bucket, filename).upload_file(Filename=os.path.join(path, file),
                                                                ExtraArgs=extra_args)
        url = f'https://{self.s3_bucket}.s3.amazonaws.com/{folder}/index.html'
        logging.info(url)
        return url

    def run(self):
        self._generate_report()
        url = self._upload_results()
        return url
