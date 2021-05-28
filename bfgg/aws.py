from typing import Optional

import boto3


class DynamoTable:
    def __init__(self, table_name: str, region_name: str, endpoint_url: str = None):
        dynamo_db = boto3.resource(
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
        return resp["items"]


class S3Bucket:
    def __init__(self, bucket_name: str, region_name: str, endpoint_url: str = None):
        s3 = boto3.resource("s3", region_name=region_name, endpoint_url=endpoint_url)
        self.bucket_name = bucket_name
        self.bucket = s3.Bucket(bucket_name)

    def upload_file(self, key: str, filename: str, extra_args: dict = None):
        self.bucket.upload_file(Key=key, Filename=filename, ExtraArgs=extra_args)
