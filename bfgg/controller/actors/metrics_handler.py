import os
from prometheus_client import Histogram, Counter
from bfgg.utils.helpers import ip_to_log_filename
from bfgg.utils.logging import logger


class MetricsHandler:

    def __init__(self, results_folder: str):
        self.logger = logger
        self.results_folder = results_folder
        self.total_users_count = Counter('gatling_total_users', "Total number of users", labelnames=['population', 'group'])
        self.total_successes_count = Counter('gatling_success_responses', "Total number of 'OK' responses",
                                             labelnames=['request_name', 'group'])
        self.total_failures_count = Counter('gatling_failure_responses', "Total number of 'KO' responses",
                                            labelnames=['request_name', 'group'])
        self.total_errors_count = Counter('gatling_errors', "Total number of error lines in the logs")
        self.total_requests_count = Counter('gatling_requests', "Total number of requests",
                                            labelnames=['request_name', 'group'])
        self.response_time_histo = Histogram('gatling_response_times', "Histogram response times for all requests",
                                             labelnames=['request_name', 'group'], unit='ms',
                                             buckets=[200, 500, 1000, 2000, 10000, float("inf")])
        self.response_time_count = Counter('gatling_response_times', "Total response time for all requests",
                                           labelnames=['request_name', 'group'])

    def handle_log(self, identity: bytes, log: bytes, group: bytes):
        self.logger.debug("Received log message")
        log = log.decode('utf-8')
        group_str = group.decode('utf-8')
        try:
            with open(os.path.join(self.results_folder,
                                   group_str,
                                   ip_to_log_filename(identity.decode('utf-8'))), 'a') as f:
                f.write(log)
        except Exception as e:
            self.logger.error(e)
        try:
            for line in log.split('\n'):
                self._create_metrics(line, group_str)
        except Exception as e:
            self.logger.error(e)

    def _create_metrics(self, log_line: str, group: str):
        try:
            if log_line.startswith('REQUEST'):
                type, iteration, _, name, start_timestamp, end_timestamp, status, errors = log_line.split('\t')
                response_time = int(end_timestamp) - int(start_timestamp)
                self.total_requests_count.labels(request_name=name, group=group).inc()
                self.response_time_histo.labels(request_name=name, group=group).observe(response_time)
                self.response_time_count.labels(request_name=name, group=group).inc(response_time)
                if status == "OK":
                    self.total_successes_count.labels(request_name=name, group=group).inc()
                else:
                    self.total_failures_count.labels(request_name=name, group=group).inc()
            elif log_line.startswith('USER'):
                type, population, user_num, start_or_end, start_timestamp, end_timestamp = log_line.split('\t')
                self.total_users_count.labels(population=population, group=group).inc()
            elif log_line.startswith('ERROR'):
                self.total_errors_count.labels(group=group).inc()
        except Exception as e:
            self.logger.error(e)
            self.logger.error(log_line)
