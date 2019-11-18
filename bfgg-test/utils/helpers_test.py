import unittest
import os
import shutil
from unittest.mock import MagicMock
from bfgg.utils.helpers import ip_to_log_filename, create_or_empty_folder


class HelpersTest(unittest.TestCase):

    def ip_to_log_filename_test(self):
        self.assertEqual("1_1_1_1.log", ip_to_log_filename("1.1.1.1"))

    def create_or_empty_folder_test_path_doesnt_exist(self):
        os.path.exists = MagicMock(return_value=False)
        os.mkdir = MagicMock()
        create_or_empty_folder("path/to/stuff")
        os.path.exists.assert_called_once()
        os.mkdir.assert_called_once_with("path/to/stuff")

    def create_or_empty_folder_test_path_folder_exists(self):
        os.path.exists = MagicMock(return_value=True)
        os.listdir = MagicMock(return_value=["A", "B", "C"])
        os.path.isfile = MagicMock(side_effect=[True, False, True])
        os.path.isdir = MagicMock(return_value=True)
        os.remove = MagicMock()
        shutil.rmtree = MagicMock()
        os.path.join = MagicMock()
        create_or_empty_folder("path/to/stuff")

        os.listdir.assert_called_once()
        self.assertEquals(3, os.path.isfile.call_count)
        os.path.isdir.assert_called_once()
        self.assertEquals(2, os.remove.call_count)
        shutil.rmtree.assert_called_once()




if __name__ == '__main__':
    unittest.main()
