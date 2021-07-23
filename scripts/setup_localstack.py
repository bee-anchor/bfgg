import boto3
from botocore.exceptions import EndpointConnectionError


def setup_dynamo(session):
    dynamo_db = session.client(
        "dynamodb", region_name="eu-west-1", endpoint_url="http://localhost:4566"
    )
    while True:
        try:
            dynamo_db.create_table(
                TableName="BfggTests",
                KeySchema=[
                    {"AttributeName": "TestId", "KeyType": "HASH"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "TestId", "AttributeType": "S"},
                    {"AttributeName": "StartTime", "AttributeType": "S"},
                    {"AttributeName": "Project", "AttributeType": "S"},
                ],
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "TimeIndex",
                        "KeySchema": [
                            {"AttributeName": "StartTime", "KeyType": "HASH"},
                            {"AttributeName": "Project", "KeyType": "RANGE"},
                        ],
                        "Projection": {
                            "ProjectionType": "ALL",
                        },
                    }
                ],
                BillingMode="PAY_PER_REQUEST",
            )
        except EndpointConnectionError as e:
            print(e)
            print("localstack not yet ready")
            continue
        else:
            print("DynamoDB table created")
            break


def setup_s3(session):
    s3 = session.resource(
        "s3", region_name="eu-west-1", endpoint_url="http://localhost:4566"
    )
    while True:
        try:
            s3.create_bucket(ACL="public-read", Bucket="bfgg-test-results")
        except EndpointConnectionError as e:
            print(e)
            print("localstack not yet ready")
            continue
        else:
            print("s3 bucket created")
            break


boto_session = boto3.session.Session(
    aws_access_key_id="example", aws_secret_access_key="example"
)
setup_dynamo(boto_session)
setup_s3(boto_session)
