#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import Request

from backend.core.conf import settings


def get_request_trace_id(request: Request) -> str:
    """
    Get the trace ID from the request header

    :param request: FastAPI request object
    :return:
    """
    return request.headers.get(settings.TRACE_ID_REQUEST_HEADER_KEY) or settings.TRACE_ID_LOG_DEFAULT_VALUE
