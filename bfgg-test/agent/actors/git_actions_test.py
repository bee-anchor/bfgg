import unittest
from unittest.mock import patch
from bfgg.agent.actors.git_actions import clone_repo
from bfgg.utils.statuses import Statuses


class MyTestCase(unittest.TestCase):

    @patch("subprocess.Popen", side_effect=FileNotFoundError)
    @patch("bfgg.agent.actors.git_actions.handle_state_change")
    def test_clone_repo_directory_doesnt_exist(self, state_change_mock, popen_mock):
        clone_repo("git@git.org:foo/bar.git", "a/b/c")
        self.assertEqual(2, state_change_mock.call_count)
        state_change_mock.assert_called_with(status=Statuses.ERROR, extra_info="Exception found when cloning. Please make sure the directory for cloning repositories exists.")

    @patch("subprocess.Popen")
    @patch("bfgg.agent.actors.git_actions.handle_state_change")
    def test_clone_repo_success(self, state_change_mock, subprocess_mock):
        subprocess_mock.return_value.communicate.return_value = b"stdout", b"""
            remote: Counting objects: 971, done.
            remote: Compressing objects: 100% (854/854), done.
            remote: Total 971 (delta 516), reused 0 (delta 0)
            Receiving objects: 100% (971/971), 99.46 KiB | 352.00 KiB/s, done.
            Resolving deltas: 100% (516/516), done.
        """
        clone_repo("git@git.org:foo/bar.git", "a/b/c")
        self.assertEqual(2, state_change_mock.call_count)
        state_change_mock.assert_called_with(status=Statuses.AVAILABLE, cloned_repo="bar")

    @patch("subprocess.Popen")
    @patch("bfgg.agent.actors.git_actions.handle_state_change")
    def test_clone_repo_already_exists(self, state_change_mock, subprocess_mock):
        subprocess_mock.return_value.communicate.side_effect = [
            (b"stdout", b"fatal: destination path '' already exists and is not an empty directory"),
            (b"stdout", b"""
                remote: Counting objects: 971, done.
                remote: Compressing objects: 100% (854/854), done.
                remote: Total 971 (delta 516), reused 0 (delta 0)
                Receiving objects: 100% (971/971), 99.46 KiB | 352.00 KiB/s, done.
                Resolving deltas: 100% (516/516), done.
            """)
        ]
        clone_repo("git@git.org:foo/bar.git", "a/b/c")
        self.assertEqual(2, state_change_mock.call_count)
        state_change_mock.assert_called_with(status=Statuses.AVAILABLE, cloned_repo="bar")

    @patch("subprocess.Popen")
    @patch("bfgg.agent.actors.git_actions.handle_state_change")
    def test_clone_repo_error(self, state_change_mock, subprocess_mock):
        subprocess_mock.return_value.communicate.return_value = b"stdout", b"""
            Repository '' not found
            fatal: Could not read from remote repository.
            
            Please make sure you have the correct access rights
            and the repository exists.
        """

        clone_repo("git@git.org:foo/bar.git", "a/b/c")
        self.assertEqual(2, state_change_mock.call_count)
        state_change_mock.assert_called_with(status=Statuses.ERROR, extra_info="Could not read from remote repository. Check agent for further details.")

if __name__ == '__main__':
    unittest.main()
