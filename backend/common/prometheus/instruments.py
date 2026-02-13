from prometheus_client import Counter, Gauge, Histogram

# Warning: This value is strongly associated with the following locations. Modifications must be updated simultaneously, otherwise Grafana indicator data query will fail.：
# - deploy/backend/grafana/fba_datasource.yml
# - deploy/backend/grafana/dashboards/fba_server.json
PROMETHEUS_APP_NAME = 'fba_server'

PROMETHEUS_REQUEST_IN_PROGRESS_GAUGE = Gauge(
    name='fba_request_in_progress',
    documentation='Measurement of statistical requests by method and path',
    labelnames=['app_name', 'method', 'path'],
)

PROMETHEUS_REQUEST_COUNTER = Counter(
    name='fba_request_total',
    documentation='Count the total number of requests by method and path',
    labelnames=['app_name', 'method', 'path'],
)

PROMETHEUS_REQUEST_COST_TIME_HISTOGRAM = Histogram(
    name='fba_request_cost_time',
    documentation='Histogram of request time taken by method and path (in ms)',
    labelnames=['app_name', 'method', 'path'],
)

PROMETHEUS_EXCEPTION_COUNTER = Counter(
    name='fba_exception_total',
    documentation='Count the total number of exceptions by method, path and exception type',
    labelnames=['app_name', 'method', 'path', 'exception_type'],
)


PROMETHEUS_RESPONSE_COUNTER = Counter(
    name='fba_response_total',
    documentation='Count the total number of responses by method, path and status code',
    labelnames=['app_name', 'method', 'path', 'status_code'],
)