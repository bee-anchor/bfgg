import json

from marshmallow import ValidationError

from bfgg.controller import create_app
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


def _base_mocker(mocker, schema=None, type=None, value=None):
    outgoing_queue_mock = mocker.patch('bfgg.controller.api.OUTGOING_QUEUE')
    if schema:
        mocker.patch(f'bfgg.controller.api.{schema}', **{
            f'return_value.load.{type}': value
        })
    return outgoing_queue_mock


def test_clone_bad_request(mocker):
    _base_mocker(mocker, 'CloneSchema', 'side_effect', ValidationError('error'))
    res = client().post('/clone', content_type="'application/json'", data=json.dumps(clone_data))
    assert 400 == res.status_code


def test_clone(mocker):
    outgoing_queue_mock = _base_mocker(mocker, 'CloneSchema', 'return_value', {'repo': repo})

    res = client().post('/clone', content_type="'application/json'", data=json.dumps(clone_data))
    assert 200 == res.status_code
    outgoing_queue_mock.put.assert_called_with(OutgoingMessage(CLONE, repo.encode('utf-8')))


def test_start_bad_request(mocker):
    _base_mocker(mocker, 'StartSchema', 'side_effect', ValidationError('error'))
    res = client().post('/start', content_type="'application/json'", data=json.dumps(start_data))
    assert 400 == res.status_code


def test_start(mocker):
    outgoing_queue_mock = _base_mocker(mocker, 'StartSchema', 'return_value', start_data)
    create_folder_mock = mocker.patch('bfgg.controller.api.create_or_empty_folder')
    res = client().post('/start', content_type="'application/json'", data=json.dumps(start_data))
    assert 200 == res.status_code
    create_folder_mock.assert_called_once()
    expected_task = f"{start_data['project']},{start_data['testClass']},{start_data['javaOpts']}".encode('utf-8')
    outgoing_queue_mock.put.assert_called_with(OutgoingMessage(START_TEST, expected_task))


def test_stop(mocker):
    outgoing_queue_mock = _base_mocker(mocker)
    res = client().post('/stop')
    assert 200 == res.status_code
    outgoing_queue_mock.put.assert_called_with(OutgoingMessage(STOP_TEST, b"STOP"))


def test_status(mocker):
    mocker.patch("bfgg.controller.api.STATE", **{
        'current_agents_state_dict.return_value': {
            "a": {"status": "AVAILABLE",
                  "cloned_repos": [],
                  "test_running": "",
                  "extra_info": ""}
        }
    })
    res = client().get('/status')
    expected = b'{"a": {"status": "AVAILABLE", "cloned_repos": [], "test_running": "", "extra_info": ""}}'
    assert 200 == res.status_code
    assert res.data == expected


def test_results(mocker):
    mocker.patch('bfgg.controller.api.ReportHandler', **{
        'return_value.run.return_value': 'http://www.example.com'
    })
    res = client().get('/results')
    assert 200 == res.status_code
    assert 'http://www.example.com' in next(res.response).decode('utf-8')
