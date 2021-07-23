from typing import Optional

import boto3


class DynamoTable:
    def __init__(
        self,
        table_name: str,
        region_name: str,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        endpoint_url: str = None,
    ):
        session = boto3.session.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        dynamo_db = session.resource(
            "dynamodb", region_name=region_name, endpoint_url=endpoint_url
        )
        self.table = dynamo_db.Table(table_name)

    def put_item(self, item: dict):
        return self.table.put_item(Item=item)

    def update_item(
        self, key: dict, update_expression: str, expression_att_values: dict
    ):
        return self.table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_att_values,
        )

    def get_item(self, key: dict) -> Optional[dict]:
        resp = self.table.get_item(Key=key)
        if "Item" in resp:
            return resp["Item"]
        else:
            return None

    def scan(self):
        resp = self.table.scan()
        return resp["Items"]


class S3Bucket:
    def __init__(
        self,
        bucket_name: str,
        region_name: str,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        endpoint_url: str = None,
    ):
        session = boto3.session.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        s3 = session.resource("s3", region_name=region_name, endpoint_url=endpoint_url)
        self.bucket_name = bucket_name
        self.bucket = s3.Bucket(bucket_name)

    def upload_file(self, key: str, filename: str, extra_args: dict = None):
        self.bucket.upload_file(Key=key, Filename=filename, ExtraArgs=extra_args)
