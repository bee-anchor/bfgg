from datetime import datetime

from bfgg.aws import DynamoTable


class DynamoTableInteractor:
    def __init__(self, table: DynamoTable):
        self.table = table

    def save_test_started(
        self,
        id: str,
        start_time: datetime,
        project: str,
        test_class: str,
        java_opts: str = None,
    ):
        item = {
            "TestId": id,
            "StartTime": start_time.isoformat(),
            "Project": project,
            "TestClass": test_class,
        }
        if java_opts:
            item["JavaOpts"] = java_opts
        self.table.put_item(item)

    def update_test_ended(self, id: str, end_time: datetime, test_results_url: str):
        self.table.update_item(
            {"TestId": id},
            "SET EndTime=:end, TestResultsUrl=:res",
            {
                ":end": end_time.isoformat(),
                ":res": test_results_url,
            },
        )

    def get_by_id(self, id: str):
        resp = self.table.get_item({"TestId": id})
        if "Item" in resp:
            return resp["Item"]
        else:
            return None

    def get_all(self):
        resp = self.table.scan()
        return resp["Items"]
