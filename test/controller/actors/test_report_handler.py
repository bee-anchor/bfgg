from bfgg.controller.actors.report_handler import ReportHandler


def test_report_handler(mocker):
    results_folder = 'a/b/c'
    gatling_folder = 'd/e/f'
    bucket = 'my_bucket'

    mocker.patch('bfgg.controller.actors.report_handler.datetime', **{
        'now.return_value.strftime.return_value': 'NOW'
    })
    mocker.patch('bfgg.controller.actors.report_handler.os.walk', **{
        'side_effect': [[
            (results_folder, ['2', '3'], ['1.html']),
            (results_folder + '/2', [], ['2.png']),
            (results_folder + '/3', [], ['3.json'])
        ]]
    })
    boto3_mock = mocker.patch('bfgg.controller.actors.report_handler.boto3').resource.return_value.Object
    subprocess_mock = mocker.patch('bfgg.controller.actors.report_handler.subprocess', **{
        'Popen.return_value.communicate.return_value': (b'Stdout', b'Stderr')
    })

    report_handler = ReportHandler(results_folder, gatling_folder, bucket, 'eu-west-1')
    result = report_handler.run()

    assert [f'{gatling_folder}/bin/gatling.sh', '-ro', results_folder] in subprocess_mock.Popen.call_args[0]

    boto3_upload_file_call_args = boto3_mock.return_value.upload_file.call_args_list

    assert boto3_mock.call_args_list[0][0] == (bucket, f'NOW/1.html')
    assert (boto3_upload_file_call_args[0][1] ==
            {'Filename': 'a/b/c/1.html', 'ExtraArgs': {'ACL': 'private', 'ContentType': 'text/html'}})

    assert boto3_mock.call_args_list[1][0] == (bucket, f'NOW/2/2.png')
    assert (boto3_upload_file_call_args[1][1] ==
            {'Filename': f'a/b/c/2/2.png', 'ExtraArgs': {'ACL': 'private', 'ContentType': 'image/png'}})

    assert boto3_mock.call_args_list[2][0] == (bucket, f'NOW/3/3.json')
    assert (boto3_upload_file_call_args[2][1] ==
            {'Filename': f'a/b/c/3/3.json', 'ExtraArgs': {'ACL': 'private', 'ContentType': 'application/json'}})

    assert result == f'https://{bucket}.s3.amazonaws.com/NOW/index.html'
