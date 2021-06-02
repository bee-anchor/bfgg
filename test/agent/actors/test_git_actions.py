from unittest.mock import call

from pytest import fixture

from bfgg.agent.utils import AgentUtils
from bfgg.agent.actors.git_actions import clone_repo
from bfgg.utils.agentstatus import AgentStatus


class TestGitActions:
    @fixture()
    def mocks(self, mocker):
        agent_utils = mocker.MagicMock(spec=AgentUtils)
        subprocess_mock = mocker.patch("subprocess.Popen")
        yield agent_utils, subprocess_mock

    def test_clone_repo_directory_doesnt_exist(self, mocks):
        agent_utils, subprocess_mock = mocks
        subprocess_mock.side_effect = FileNotFoundError
        clone_repo("git@git.org:foo/bar.git", "a/b/c", agent_utils)
        agent_utils.handle_state_change.assert_called_once_with(
            status=AgentStatus.ERROR,
            extra_info="Exception found when cloning. Please make sure the directory "
            "for cloning repositories exists.",
        )

    def test_clone_repo_success(self, mocks):
        agent_utils, subprocess_mock = mocks
        subprocess_mock.return_value.communicate.return_value = (
            b"stdout",
            b"""
                remote: Counting objects: 971, done.
                remote: Compressing objects: 100% (854/854), done.
                remote: Total 971 (delta 516), reused 0 (delta 0)
                Receiving objects: 100% (971/971), 99.46 KiB | 352.00 KiB/s, done.
                Resolving deltas: 100% (516/516), done.
            """,
        )
        clone_repo("git@git.org:foo/bar.git", "a/b/c", agent_utils)
        assert 2 == agent_utils.handle_state_change.call_count
        agent_utils.handle_state_change.assert_has_calls(
            [
                call(status=AgentStatus.CLONING),
                call(status=AgentStatus.AVAILABLE, cloned_repo={"bar"}),
            ]
        )

    def test_clone_repo_already_exists(self, mocks):
        agent_utils, subprocess_mock = mocks
        subprocess_mock.return_value.communicate.side_effect = [
            (
                b"stdout",
                b"fatal: destination path '' already exists and is not an empty directory",
            ),
            (
                b"stdout",
                b"""
                    remote: Counting objects: 971, done.
                    remote: Compressing objects: 100% (854/854), done.
                    remote: Total 971 (delta 516), reused 0 (delta 0)
                    Receiving objects: 100% (971/971), 99.46 KiB | 352.00 KiB/s, done.
                    Resolving deltas: 100% (516/516), done.
                """,
            ),
        ]
        clone_repo("git@git.org:foo/bar.git", "a/b/c", agent_utils)
        assert 2 == agent_utils.handle_state_change.call_count
        agent_utils.handle_state_change.assert_has_calls(
            [
                call(status=AgentStatus.CLONING),
                call(status=AgentStatus.AVAILABLE, cloned_repo={"bar"}),
            ]
        )

    def test_clone_repo_error(self, mocks):
        agent_utils, subprocess_mock = mocks
        subprocess_mock.return_value.communicate.return_value = (
            b"stdout",
            b"""
                Repository '' not found
                fatal: Could not read from remote repository.

                Please make sure you have the correct access rights
                and the repository exists.
            """,
        )

        clone_repo("git@git.org:foo/bar.git", "a/b/c", agent_utils)
        assert 2 == agent_utils.handle_state_change.call_count
        agent_utils.handle_state_change.assert_has_calls(
            [
                call(status=AgentStatus.CLONING),
                call(
                    status=AgentStatus.ERROR,
                    extra_info="Could not read from remote repository. Check agent for "
                    "further details.",
                ),
            ]
        )
