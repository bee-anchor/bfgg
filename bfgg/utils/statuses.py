from enum import Enum

class Statuses(Enum):
    AVAILABLE = "Available"
    CLONE_ERROR = "Clone Error"
    TEST_RUNNING = "Test Running"
    TEST_STOPPED = "Test Stopped"
    TEST_FINISHED = "Test Finished"
    TEST_ERROR = "Test Error"
    CLONING = "Cloning"
