import json
from unittest.mock import patch
from marshmallow import ValidationError
from bfgg.controller import create_app
from bfgg.utils.statuses import Statuses
from bfgg.utils.messages import OutgoingMessage, CLONE, START_TEST, STOP_TEST

repo = "git@bitbucket.org:blah/bleh.git"
clone_data = {'repo': repo}
start_data = {
    'project': repo,
    'testClass': 'FullTest',
    'javaOpts': '-Xmx14G -DCONFIG1=500 -DCONFIG2=999999'
}
app = create_app()
app.testing = True
client = app.test_client

@patch('bfgg.controller.api.OUTGOING_QUEUE')
@patch('bfgg.controller.api.CloneSchema', **{
    'return_value.load.side_effect': ValidationError('error')
})
def test_clone_bad_request(clone_schema_mock, outgoing_queue_mock):
    res = client().post('/clone', content_type="'application/json'", data=json.dumps(clone_data))
    assert 400 == res.status_code

@patch('bfgg.controller.api.OUTGOING_QUEUE')
@patch('bfgg.controller.api.CloneSchema', **{
    'return_value.load.return_value': {
        'repo': repo
    }
})
def test_clone(clone_schema_mock, outgoing_queue_mock):
    res = client().post('/clone', content_type="'application/json'", data=json.dumps(clone_data))
    assert 200 == res.status_code
    outgoing_queue_mock.put.assert_called_with(OutgoingMessage(CLONE, repo.encode('utf-8')))

@patch('bfgg.controller.api.OUTGOING_QUEUE')
@patch('bfgg.controller.api.StartSchema', **{
    'return_value.load.side_effect': ValidationError('error')
})
def test_start_bad_request(start_schema_mock, outgoing_queue_mock):
    res = client().post('/start', content_type="'application/json'", data=json.dumps(start_data))
    assert 400 == res.status_code

@patch('bfgg.controller.api.OUTGOING_QUEUE')
@patch('bfgg.controller.api.StartSchema', **{
    'return_value.load.return_value': start_data
})
@patch('bfgg.controller.api.create_or_empty_folder')
def test_start(create_folder_mock, start_schema_mock, outgoing_queue_mock):
    res = client().post('/start', content_type="'application/json'", data=json.dumps(start_data))
    assert 200 == res.status_code
    create_folder_mock.assert_called_once()
    expected_task = f"{start_data['project']},{start_data['testClass']},{start_data['javaOpts']}".encode('utf-8')
    outgoing_queue_mock.put.assert_called_with(OutgoingMessage(START_TEST, expected_task))

@patch('bfgg.controller.api.OUTGOING_QUEUE')
def test_stop(outgoing_queue_mock):
    res = client().post('/stop')
    assert 200 == res.status_code
    outgoing_queue_mock.put.assert_called_with(OutgoingMessage(STOP_TEST, b"STOP"))

# /status uses a custom deserialiser so test is checking a few different json types just to make sure it behaves
# as expected
@patch("bfgg.controller.api.STATE", **{
    'current_agents_state.return_value': {
        "a": {1, 2, 3},
        "b": Statuses.TEST_FINISHED,
        "c": [1, 2, 3],
        "d": {
            "d1": 123,
            "d2": "123"
        }
    }
})
def test_status(state_mock):
    res = client().get('/status')
    expected = {
        "a": [1,2,3],
        "b": "TEST_FINISHED",
        "c": [1,2,3],
        "d": {
            "d1": 123,
            "d2": "123"
        }
    }
    assert 200 == res.status_code
    assert expected == json.loads(res.data)

@patch('bfgg.controller.api.ReportHandler', **{
    'return_value.run.return_value': 'http://www.example.com'
})
def test_results(report_handler_mock):
    res = client().get('/results')
    assert 200 == res.status_code
    assert 'http://www.example.com' in next(res.response).decode('utf-8')