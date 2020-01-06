from bfgg.controller.actors.report_handler import ReportHandler


class TestReportHandler:
    results_folder = 'a/b/c'
    group = 'ungrouped'
    group_results_folder = f'a/b/c/{group}'
    gatling_folder = 'd/e/f'
    bucket = 'my_bucket'
    report_handler = ReportHandler(results_folder, gatling_folder, bucket, 'eu-west-1', group)

    def test_content_type_from_file(self):
        assert self.report_handler._content_type_from_file('some_file.js') == 'application/javascript'

    def test_generate_report(self, mocker):
        subprocess_mock = mocker.patch('bfgg.controller.actors.report_handler.subprocess', **{
            'Popen.return_value.communicate.return_value': (b'Stdout', b'Stderr')
        })
        logging_mock = mocker.MagicMock()
        self.report_handler.logger = logging_mock

        self.report_handler._generate_report()
        assert [f'{self.gatling_folder}/bin/gatling.sh', '-ro',
                self.group_results_folder] in subprocess_mock.Popen.call_args[0]
        logging_mock.info.assert_has_calls([
            mocker.call([f'{self.gatling_folder}/bin/gatling.sh', '-ro', self.group_results_folder]),
            mocker.call('Stdout')
        ])

    def test_upload_results(self, mocker):
        mocker.patch('bfgg.controller.actors.report_handler.datetime', **{
            'now.return_value.strftime.return_value': 'NOW'
        })
        mocker.patch('bfgg.controller.actors.report_handler.os.walk', **{
            'side_effect': [[
                (self.group_results_folder, ['2', '3'], ['1.html']),
                (self.group_results_folder + '/2', [], ['2.png']),
                (self.group_results_folder + '/3', [], ['3.json'])
            ]]
        })
        mocker.patch('bfgg.controller.actors.report_handler.shutil')
        boto3_mock = mocker.patch('bfgg.controller.actors.report_handler.boto3').resource.return_value.Object
        logging_mock = mocker.patch('bfgg.controller.actors.report_handler.logger')

        assert self.report_handler._upload_results() == f'https://{self.bucket}.s3.amazonaws.com/NOW/index.html'
        logging_mock.info.asser_called_with(f'https://{self.bucket}.s3.amazonaws.com/NOW/index.html')

        boto3_upload_file_call_args = boto3_mock.return_value.upload_file.call_args_list
        assert boto3_mock.call_args_list[0][0] == (self.bucket, f'NOW/1.html')
        assert (boto3_upload_file_call_args[0][1] ==
                {'Filename': 'a/b/c/ungrouped/1.html', 'ExtraArgs': {'ACL': 'private', 'ContentType': 'text/html'}})
        assert boto3_mock.call_args_list[1][0] == (self.bucket, f'NOW/2/2.png')
        assert (boto3_upload_file_call_args[1][1] ==
                {'Filename': f'a/b/c/ungrouped/2/2.png', 'ExtraArgs': {'ACL': 'private', 'ContentType': 'image/png'}})
        assert boto3_mock.call_args_list[2][0] == (self.bucket, f'NOW/3/3.json')
        assert (boto3_upload_file_call_args[2][1] ==
                {'Filename': f'a/b/c/ungrouped/3/3.json',
                 'ExtraArgs': {'ACL': 'private', 'ContentType': 'application/json'}})
