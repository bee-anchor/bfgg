import logging.config
import subprocess
import os
from bfgg.agent.model import handle_state_change
from bfgg.utils.statuses import Statuses


def clone_repo(project: str, tests_location: str):
    project_name = project[project.find('/') + 1: project.find('.git')]
    logging.info(f"Getting {project}")
    try :
        resp = subprocess.Popen(['git', 'clone', project, '--progress'],
                            cwd=tests_location,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    except FileNotFoundError as e:
        logging.error("Directory for cloning doesn't exist")
        handle_state_change(status=Statuses.CLONE_ERROR.value, extra_info="Exception found when cloning. Please make sure the directory for cloning repositories exists.")
        return
    handle_state_change(status=Statuses.CLONING.value)
    stdout, stderror = resp.communicate()
    stdout = stdout.decode('utf-8')
    stderror = stderror.decode('utf-8')
    if "Receiving objects: 100%" in stderror:
        handle_state_change(status=Statuses.AVAILABLE.value, cloned_repo=project_name, extra_info="None")
        logging.info(f"Cloned {project_name}")
    elif "already exists and is not an empty directory" in stderror:
        command = (f"git -C {os.path.join(tests_location, project_name)} fetch && "
                   f"git -C {os.path.join(tests_location, project_name)} reset origin/master --hard")
        resp = subprocess.Popen(command,
                                shell=True,
                                cwd=f"{tests_location}/{project_name}",
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        stdout, stderror = resp.communicate()
        stdout = stdout.decode('utf-8')
        handle_state_change(status=Statuses.AVAILABLE.value, cloned_repo=project_name, extra_info="None")
        logging.info(f"Got latest {project_name}")
    elif "fatal: Could not read from remote repository" in stderror:
        logging.error(stderror)
        handle_state_change(status=Statuses.CLONE_ERROR.value, extra_info="Could not read from remote repository. Check agent for further details.")
    _log_if_present(stdout)
    _log_if_present(stderror)


def _log_if_present(std):
    if std:
        logging.debug(std)