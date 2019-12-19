import os
import logging.config
from prometheus_client import Histogram, Counter
from bfgg.utils.helpers import ip_to_log_filename


class MetricsHandler:

    def __init__(self, results_folder: str):
        self.results_folder = results_folder
        self.total_users_count = Counter('gatling_total_users', "Total number of users", labelnames=['population'])
        self.total_successes_count = Counter('gatling_success_responses', "Total number of 'OK' responses",
                                             labelnames=['request_name'])
        self.total_failures_count = Counter('gatling_failure_responses', "Total number of 'KO' responses",
                                            labelnames=['request_name'])
        self.total_errors_count = Counter('gatling_errors', "Total number of error lines in the logs")
        self.total_requests_count = Counter('gatling_requests', "Total number of requests",
                                            labelnames=['request_name'])
        self.response_time_histo = Histogram('gatling_response_times', "Histogram response times for all requests",
                                             labelnames=['request_name'], unit='ms',
                                             buckets=[200, 500, 1000, 2000, 10000, float("inf")])
        self.response_time_count = Counter('gatling_response_times', "Total response time for all requests",
                                           labelnames=['request_name'])

    def handle_log(self, identity: bytes, log: bytes, group: bytes):
        logging.debug("Received log message")
        log = log.decode('utf-8')
        with open(os.path.join(self.results_folder,
                               group.decode('utf-8'),
                               ip_to_log_filename(identity.decode('utf-8'))), 'a') as f:
            f.write(log)
        for line in log.split('\n'):
            self._create_metrics(line)

    def _create_metrics(self, log_line):
        try:
            if log_line.startswith('REQUEST'):
                type, iteration, _, name, start_timestamp, end_timestamp, status, errors = log_line.split('\t')
                response_time = int(end_timestamp) - int(start_timestamp)
                self.total_requests_count.labels(request_name=name).inc()
                self.response_time_histo.labels(request_name=name).observe(response_time)
                self.response_time_count.labels(request_name=name).inc(response_time)
                if status == "OK":
                    self.total_successes_count.labels(request_name=name).inc()
                else:
                    self.total_failures_count.labels(request_name=name).inc()
            elif log_line.startswith('USER'):
                type, population, user_num, start_or_end, start_timestamp, end_timestamp = log_line.split('\t')
                self.total_users_count.labels(population=population).inc()
            elif log_line.startswith('ERROR'):
                self.total_errors_count.inc()
        except Exception as e:
            logging.error(e)
            logging.error(log_line)
