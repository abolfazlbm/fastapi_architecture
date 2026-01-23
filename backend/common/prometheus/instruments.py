from prometheus_client import Counter, Gauge, Histogram

from backend.core.conf import settings

PROMETHEUS_INFO_GAUGE = (
    Gauge(name='fba_app_info', documentation='fba application information', labelnames=['app_name'])
    .labels(app_name=settings.GRAFANA_APP_NAME)
    .inc()
)

PROMETHEUS_REQUEST_IN_PROGRESS_GAUGE = Gauge(
    'fba_request_in_progress',
    'Measurement of statistical requests by method and path',
    ['app_name', 'method', 'path'],
)

PROMETHEUS_REQUEST_COUNTER = Counter('fba_request_total', 'Count the total number of requests by method and path', ['app_name', 'method', 'path'])

PROMETHEUS_RESPONSE_COUNTER = Counter(
    'fba_response_total',
    'Count the total number of responses by method, path and status code',
    ['app_name', 'method', 'path', 'status_code'],
)

PROMETHEUS_EXCEPTION_COUNTER = Counter(
    'fba_exception_total',
    'Count the total number of exceptions by method, path and exception type',
    ['app_name', 'method', 'path', 'exception_type'],
)

PROMETHEUS_REQUEST_COST_TIME_HISTOGRAM = Histogram(
    'fba_request_cost_time',
    'Histogram of request time taken by method and path (in ms)',
    ['app_name', 'method', 'path'],
)