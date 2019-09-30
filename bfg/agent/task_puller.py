import threading
import zmq
import subprocess
from bfg.utils.messages import CLONE
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
            else:
                print(type, identity, message)

    def clone_repo(self, project: str):
        print(f"Cloning {project}")
        resp = subprocess.Popen(['git', 'clone', f'git@bitbucket.org:infinityworksconsulting/{project}.git'],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        stdout, stderror = resp.communicate()
        stdout = stdout.decode('utf-8')
        if f"destination path '{project}' already exists and is not an empty directory" in stdout:
            print("Already cloned")
            self.lock.acquire()
            self.state.status = "Cloned"
            self.lock.release()
            return
        elif f"Cloning into '{project}'" in stdout:
            print("Cloned successfully")
            self.lock.acquire()
            self.state.status = "Cloned"
            self.lock.release()
            return
        else:
            print(stdout, stderror)

