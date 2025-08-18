#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from backend.common.log import log
from backend.utils.timezone import timezone


class AccessMiddleware(BaseHTTPMiddleware):
    """Access log middleware"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        Process requests and log access logs

        :param request: FastAPI request object
        :param call_next: next middleware or routing processing function
        :return:
        """
        path = request.url.path if not request.url.query else request.url.path + '/' + request.url.query

        if request.method != 'OPTIONS':
            log.debug(f'--> Request to begin[{path}]')

        perf_time = time.perf_counter()
        request.state.perf_time = perf_time

        start_time = timezone.now()
        request.state.start_time = start_time

        response = await call_next(request)

        elapsed = (time.perf_counter() - perf_time) * 1000

        if request.method != 'OPTIONS':
            log.debug('<-- Request ends')

            log.info(
                f'{request.client.host: <15} | {request.method: <8} | {response.status_code: <6} | '
                f'{path} | {elapsed:.3f}ms'
            )

        return response
