import uuid

class State:

    def __init__(self):
        self.identity = str(uuid.uuid1()).encode('UTF-8')
        # one of: Started, Registered, Cloned, Ready, Test_Running
        self.status = "Started"
