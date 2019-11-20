from unittest.mock import patch, mock_open
from bfgg.controller.actors.report_handler import ReportHandler

@patch('bfgg.controller.actors.report_handler.subprocess', **{
    'Popen.return_value.communicate.return_value': (b"Stdout", b"Stderr")
})
@patch('bfgg.controller.actors.report_handler.os', **{
    'listdir.side_effect': [["1.html", "2", "3"], ["2.png"], ["3.json"]],
    'path.isfile.side_effect': [True, False, False],
    'path.isdir.return_value': True
})
@patch('bfgg.controller.actors.report_handler.boto3')
@patch('bfgg.controller.actors.report_handler.datetime', **{
    'now.return_value.strftime.return_value': "NOW"
})
@patch('builtins.open', mock_open(read_data="aabbcc"))
def test_report_handler(datetime_mock, boto3_mock, os_mock, subprocess_mock):
    results_folder = "a/b/c"
    gatling_folder = "d/e/f"
    bucket = 'my_bucket'
    report_handler = ReportHandler(results_folder, gatling_folder, bucket, 'eu-west-1')
    result = report_handler.run()

    assert [f'{gatling_folder}/bin/gatling.sh', '-ro', results_folder] in subprocess_mock.Popen.call_args[0]
    boto3_put_object_call_args = boto3_mock.resource.return_value.Bucket.return_value.put_object.call_args_list
    assert {'Key': f'NOW/1.html', 'Body': 'aabbcc', 'ACL': 'private', 'ContentType': 'text/html'} == boto3_put_object_call_args[0][1]
    assert {'Key': f'NOW/2/2.png', 'Body': 'aabbcc', 'ACL': 'private', 'ContentType': 'image/png'} == boto3_put_object_call_args[1][1]
    assert {'Key': f'NOW/3/3.json', 'Body': 'aabbcc', 'ACL': 'private', 'ContentType': 'application/json'} == boto3_put_object_call_args[2][1]
    assert f'https://{bucket}.s3.amazonaws.com/NOW/index.html' == result