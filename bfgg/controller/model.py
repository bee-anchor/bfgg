import threading
import zmq
import os
from queue import Queue
from bfgg.controller.state import State
from dotenv import load_dotenv
from bfgg.controller.actors.dynamodb_resource import DynamoDbResource

load_dotenv()
LOCK = threading.Lock()
STATE = State(LOCK)
CONTEXT = zmq.Context()
OUTGOING_QUEUE = Queue()
INCOMING_PORT = os.getenv("CONTROLLER_MESSAGING_PORT")
OUTGOING_PORT = os.getenv("AGENT_MESSAGING_PORT")
RESULTS_FOLDER = os.getenv("RESULTS_FOLDER")
GATLING_LOCATION = os.getenv("GATLING_LOCATION")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_REGION = os.getenv("S3_REGION")
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE")
DYNAMO_DB = DynamoDbResource(DYNAMODB_TABLE)
