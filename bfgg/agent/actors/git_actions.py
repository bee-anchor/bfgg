import os
import subprocess
import logging

from bfgg.agent.utils import AgentUtils
from bfgg.utils.agentstatus import AgentStatus

logger = logging.getLogger(__name__)


def clone_repo(project: str, tests_location: str, agent_utils: AgentUtils):
    project_name = project[project.find("/") + 1 : project.find(".git")]
    agent_utils.ensure_tests_folder()
    logger.info(f"Getting {project}")
    resp = subprocess.Popen(
        ["git", "clone", project, "--progress"],
        cwd=tests_location,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    agent_utils.handle_state_change(status=AgentStatus.CLONING)
    stdout, stderror = resp.communicate()
    stdout = stdout.decode("utf-8")
    stderror = stderror.decode("utf-8")
    if "Receiving objects: 100%" in stderror:
        agent_utils.handle_state_change(
            status=AgentStatus.AVAILABLE, cloned_repo={project_name}
        )
        logger.info(f"Cloned {project_name}")
    elif "already exists and is not an empty directory" in stderror:
        command = (
            f"git -C {os.path.join(tests_location, project_name)} fetch && "
            f"git -C {os.path.join(tests_location, project_name)} reset origin/master --hard"
        )
        resp = subprocess.Popen(
            command,
            shell=True,
            cwd=f"{tests_location}/{project_name}",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        stdout, stderror = resp.communicate()
        stdout = stdout.decode("utf-8")
        logger.info(project_name)
        agent_utils.handle_state_change(
            status=AgentStatus.AVAILABLE, cloned_repo={project_name}
        )
        logger.info(f"Got latest {project_name}")
    elif "fatal: Could not read from remote repository" in stderror:
        agent_utils.handle_state_change(
            status=AgentStatus.ERROR,
            extra_info=stderror,
        )
        logger.error(stderror)
    _debug_log_if_present(stdout)
    _debug_log_if_present(stderror)


def _debug_log_if_present(std):
    if std:
        logger.debug(std)
