import boto3
from datetime import datetime


class DynamoDbResource:

    def __init__(self, table: str):
        dynamo_db = boto3.resource('dynamodb')
        self.table = dynamo_db.Table(table)

    def save_test_started(self, id: str, start_time: datetime, project: str, test_class: str, java_opts: str = None):
        item = {
            'TestId': id,
            'StartTime': start_time.isoformat(),
            'Project': project,
            'TestClass': test_class,
        }
        if java_opts:
            item['JavaOpts'] = java_opts
        self.table.put_item(Item=item)

    def update_test_ended(self, id: str, end_time: datetime, test_results_url: str):
        self.table.update_item(
            Key={'TestId': id},
            UpdateExpression="SET EndTime=:end, TestResultsUrl=:res",
            ExpressionAttributeValues={':end': end_time.isoformat(), ':res': test_results_url}
        )

    def get_by_id(self, id: str):
        resp = self.table.get_item(Key={
            'TestId': id
        })
        if 'Item' in resp:
            return resp['Item']
        else:
            return None

    def get_all(self):
        resp = self.table.scan()
        return resp['Items']
