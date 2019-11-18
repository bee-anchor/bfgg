import unittest
from unittest.mock import patch
from bfgg.utils.helpers import ip_to_log_filename, create_or_empty_folder


class HelpersTest(unittest.TestCase):

    def test_ip_to_log_filename(self):
        self.assertEqual("1_1_1_1.log", ip_to_log_filename("1.1.1.1"))

    @patch('os.path.exists', return_value=False)
    @patch('os.mkdir')
    def test_create_or_empty_folder_test_path_doesnt_exist(self, os_mkdir_mock, os_path_exists_mock):
        create_or_empty_folder("path/to/stuff")
        os_path_exists_mock.assert_called_once()
        os_mkdir_mock.assert_called_once_with("path/to/stuff")

    @patch('shutil.rmtree')
    @patch('os.listdir', return_value=["A", "B", "C"])
    @patch('os.remove')
    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', side_effect=[True, False, True])
    @patch('os.path.isdir', return_value=True)
    @patch('os.path.join')
    def test_create_or_empty_folder_test_path_folder_exists(self, os_path_join_mock, os_path_isdir_mock,
                                                            os_path_isfile_mock, os_path_exists_mock, os_remove_mock,
                                                            os_listdir_mock, shutil_rmtree_mock):
        create_or_empty_folder("path/to/stuff")

        os_listdir_mock.assert_called_once()
        self.assertEqual(3, os_path_isfile_mock.call_count)
        os_path_isdir_mock.assert_called_once()
        self.assertEqual(2, os_remove_mock.call_count)
        shutil_rmtree_mock.assert_called_once()




if __name__ == '__main__':
    unittest.main()
