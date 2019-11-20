import unittest
from unittest.mock import patch
from bfgg.utils.helpers import ip_to_log_filename, create_or_empty_folder


class HelpersTest(unittest.TestCase):

    def test_ip_to_log_filename(self):
        self.assertEqual("1_1_1_1.log", ip_to_log_filename("1.1.1.1"))

    @patch('bfgg.utils.helpers.os', **{'path.exists.return_value': False})
    def test_create_or_empty_folder_test_path_doesnt_exist(self, os_mock):
        create_or_empty_folder("path/to/stuff")
        os_mock.path.exists.assert_called_once()
        os_mock.mkdir.assert_called_once_with("path/to/stuff")

    @patch('bfgg.utils.helpers.shutil.rmtree')
    @patch('bfgg.utils.helpers.os', **{
        'listdir.return_value': ["A", "B", "C"],
        'path.exists.return_value': True,
        'path.isfile.side_effect': [True, False, True],
        'path.isdir.return_value': True
    })
    def test_create_or_empty_folder_test_path_folder_exists(self, os_mock, shutil_mock):

        create_or_empty_folder("path/to/stuff")

        os_mock.listdir.assert_called_once()
        os_mock.path.isdir.assert_called_once()
        self.assertEqual(2, os_mock.remove.call_count)
        shutil_mock.assert_called_once()

if __name__ == '__main__':
    unittest.main()
