
class State:

    def __init__(self, identity: str):
        self.identity = identity.encode('utf-8')
        # one of: Started, Registered, Cloned, Ready, Test_Running, Test_Finished
        self.status = "Started"
        self.project = None
        self.test = None
