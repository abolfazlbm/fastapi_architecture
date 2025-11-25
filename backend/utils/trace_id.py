from backend.common.context import ctx
from backend.core.conf import settings


def get_request_trace_id() -> str:
    """Get tracking ID from request header"""
    if ctx.exists():
        return ctx.get(settings.TRACE_ID_REQUEST_HEADER_KEY, settings.TRACE_ID_LOG_DEFAULT_VALUE)
    return settings.TRACE_ID_LOG_DEFAULT_VALUE
