
class State:

    def __init__(self, identity: str):
        self.identity: bytes = identity.encode('utf-8')
        # one of: Started, Registered, Cloned, Ready, Test_Running, Test_Finished
        self.status: str = "Started"
        self.project: str = None
        self.test: str = None
