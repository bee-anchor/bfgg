import threading
import zmq
import subprocess
from pathlib import Path
from bfg.utils.messages import CLONE, START_TEST
from bfg.agent.state import State


class TaskHandler(threading.Thread):

    def __init__(self, lock: threading.Lock, state: State, context: zmq.Context, controller_host: str, port: str):
        threading.Thread.__init__(self)
        self.lock = lock
        self.state = state
        self.context = context
        self.controller_host = controller_host
        self.port = port

    def run(self):
        handler = self.context.socket(zmq.PULL)
        handler.connect(f"tcp://{self.controller_host}:{self.port}")
        print("TaskHandler thread started")
        while True:
            [type, identity, message] = handler.recv_multipart()
            if type == CLONE:
                self.clone_repo(message.decode("utf-8"))
            elif type == START_TEST:
                self.start_test(message.decode('utf-8'))
            else:
                print(type, identity, message)

    def clone_repo(self, project: str):
        print(f"Getting {project}")
        self.state.project = project
        resp = subprocess.Popen(['git', 'clone', f'git@bitbucket.org:infinityworksconsulting/{project}.git'],
                                cwd=str(Path.home()),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        stdout, stderror = resp.communicate()
        stdout = stdout.decode('utf-8')
        if f"Cloning into '{project}'" in stdout:
            self.lock.acquire()
            self.state.status = "Cloned"
            self.lock.release()
        elif f"destination path '{project}' already exists and is not an empty directory" in stdout:
            resp = subprocess.Popen(['git', 'pull'],
                                    cwd=f"{str(Path.home())}/{project}",
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            stdout, stderror = resp.communicate()
            stdout = stdout.decode('utf-8')
        print(stdout, stderror)

    def start_test(self, test: str):
        self.lock.acquire()
        project = self.state.project
        self.state.status = "Test_Running"
        self.lock.release()
        print(f"Starting test {test}")
        test_run = subprocess.Popen(['sbt', 'gatling:testOnly', test],
                                    cwd=f"{str(Path.home())}/{project}",
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
        stdout, stderror = test_run.communicate()
        if stdout and type(stdout) == bytes:
            stdout = stdout.decode('utf-8')
        if stderror and type(stderror) == bytes:
            stderror = stderror.decode('utf-8')
        return_code = test_run.poll()
        print(stdout, stderror, return_code)
        self.lock.acquire()
        self.state.status = "Ready"
        self.lock.release()
