from os import getenv
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class Config:
    log_level: str
    controller_host: str
    agent_messaging_port: int
    controller_messaging_port: int
    tests_location: str
    results_folder: str
    gatling_location: str
    agent_identity: str
    log_send_interval: float
    s3_bucket: str
    dynamodb_table: str
    s3_region: str
    aws_default_region: str
    aws_endpoint_url: str


load_dotenv()
config = Config(
    getenv("LOG_LEVEL", "INFO"),
    getenv("CONTROLLER_HOST"),
    getenv("AGENT_MESSAGING_PORT", 9501),
    getenv("CONTROLLER_MESSAGING_PORT", 9502),
    getenv("TESTS_LOCATION"),
    getenv("RESULTS_FOLDER"),
    getenv("GATLING_LOCATION"),
    getenv("AGENT_IDENTITY"),
    getenv("LOG_SEND_INTERVAL", 1),
    getenv("S3_BUCKET"),
    getenv("DYNAMODB_TABLE"),
    getenv("S3_REGION", "eu-west-1"),
    getenv("AWS_DEFAULT_REGION", "eu-west-1"),
    getenv("AWS_ENDPOINT_URL", None),
)
