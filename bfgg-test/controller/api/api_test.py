import unittest
import json
from unittest.mock import patch
from marshmallow import ValidationError
from bfgg.controller import create_app
from bfgg.utils.statuses import Statuses
from bfgg.utils.messages import OutgoingMessage, CLONE, START_TEST


class ApiTest(unittest.TestCase):
    repo = "git@bitbucket.org:blah/bleh.git"
    clone_data = {'repo': repo}
    start_data = {
        'project': repo,
        'testClass': 'FullTest',
        'javaOpts': '-Xmx14G -DCONFIG1=500 -DCONFIG2=999999'
    }

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client

    @patch('bfgg.controller.api.OUTGOING_QUEUE')
    @patch('bfgg.controller.api.CloneSchema', **{
        'return_value.load.side_effect': ValidationError('error')
    })
    def test_clone_bad_request(self, clone_schema_mock, outgoing_queue_mock):
        res = self.client().post('/clone', content_type="'application/json'", data=json.dumps(self.clone_data))
        self.assertEqual(400, res.status_code)

    @patch('bfgg.controller.api.OUTGOING_QUEUE')
    @patch('bfgg.controller.api.CloneSchema', **{
        'return_value.load.return_value': {
            'repo': repo
        }
    })
    def test_clone(self, clone_schema_mock, outgoing_queue_mock):
        res = self.client().post('/clone', content_type="'application/json'", data=json.dumps(self.clone_data))
        self.assertEqual(200, res.status_code)
        outgoing_queue_mock.put.assert_called_with(OutgoingMessage(CLONE, self.repo.encode('utf-8')))

    @patch('bfgg.controller.api.OUTGOING_QUEUE')
    @patch('bfgg.controller.api.StartSchema', **{
        'return_value.load.side_effect': ValidationError('error')
    })
    def test_start_bad_request(self, start_schema_mock, outgoing_queue_mock):
        res = self.client().post('/start', content_type="'application/json'", data=json.dumps(self.start_data))
        self.assertEqual(400, res.status_code)

    @patch('bfgg.controller.api.OUTGOING_QUEUE')
    @patch('bfgg.controller.api.StartSchema', **{
        'return_value.load.return_value': start_data
    })
    @patch('bfgg.controller.api.create_or_empty_folder')
    def test_start(self, create_folder_mock, start_schema_mock, outgoing_queue_mock):
        res = self.client().post('/start', content_type="'application/json'", data=json.dumps(self.start_data))
        self.assertEqual(200, res.status_code)
        create_folder_mock.assert_called_once()
        expected_task = f"{self.start_data['project']},{self.start_data['testClass']},{self.start_data['javaOpts']}".encode('utf-8')
        outgoing_queue_mock.put.assert_called_with(OutgoingMessage(START_TEST, expected_task))

    # /status uses a custom deserialiser so test is checking a few different json types just to make sure it behaves as expected
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
    def test_status(self, state_mock):
        res = self.client().get('/status')
        expected = {
            "a": [1,2,3],
            "b": "TEST_FINISHED",
            "c": [1,2,3],
            "d": {
                "d1": 123,
                "d2": "123"
            }
        }
        self.assertEqual(200, res.status_code)
        self.assertDictEqual(expected, json.loads(res.data))




if __name__ == '__main__':
    unittest.main()
