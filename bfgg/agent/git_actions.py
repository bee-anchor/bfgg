import logging.config
import subprocess
import os
from bfgg.agent.state import State
from threading import Lock


def clone_repo(project: str, tests_location: str, lock: Lock, state: State):
    project_name = project[project.find('/') + 1: project.find('.git')]
    logging.info(f"Getting {project}")
    resp = subprocess.Popen(['git', 'clone', project],
                            cwd=tests_location,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    stdout, stderror = resp.communicate()
    stdout = stdout.decode('utf-8')
    if f"Cloning into '{project_name}'" in stdout:
        with lock:
            state.status = "Cloned"
        logging.info(f"Cloned {project_name}")
    elif f"already exists and is not an empty directory" in stdout:
        command = (f"git -C {os.path.join(tests_location, project_name)} fetch && "
                   f"git -C {os.path.join(tests_location, project_name)} reset origin/master --hard")
        resp = subprocess.Popen(command,
                                shell=True,
                                cwd=f"{tests_location}/{project_name}",
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        stdout, stderror = resp.communicate()
        stdout = stdout.decode('utf-8')
        with lock:
            state.status = "Cloned"
        logging.info(f"Got latest {project_name}")
    logging.debug(stdout)
