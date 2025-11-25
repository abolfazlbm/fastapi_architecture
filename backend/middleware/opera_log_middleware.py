import time

from asyncio import Queue
from typing import Any

from asgiref.sync import sync_to_async
from fastapi import Response
from starlette.datastructures import UploadFile
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from backend.app.admin.schema.opera_log import CreateOperaLogParam
from backend.app.admin.service.opera_log_service import opera_log_service
from backend.common.context import ctx
from backend.common.enums import OperaLogCipherType, StatusType
from backend.common.log import log
from backend.common.queue import batch_dequeue
from backend.common.response.response_code import StandardResponseCode
from backend.core.conf import settings
from backend.database.db import async_db_session
from backend.utils.encrypt import AESCipher, ItsDCipher, Md5Cipher
from backend.utils.trace_id import get_request_trace_id


class OperaLogMiddleware(BaseHTTPMiddleware):
    """Operation log middleware"""

    opera_log_queue: Queue = Queue(maxsize=100000)

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """
        Process requests and log operation logs

        :param request: FastAPI request object
        :param call_next: next middleware or routing processing function
        :return:
        """
        response = None
        path = request.url.path

        if path in settings.OPERA_LOG_PATH_EXCLUDE or not path.startswith(f'{settings.FASTAPI_API_V1_PATH}'):
            response = await call_next(request)
        else:
            method = request.method
            args = await self.get_request_args(request)

            # Execute a request
            code = 200
            msg = 'Success'
            status = StatusType.enable
            error = None
            try:
                response = await call_next(request)
                elapsed = round((time.perf_counter() - ctx.perf_time) * 1000, 3)
                for e in [
                    '__request_http_exception__',
                    '__request_validation_exception__',
                    '__request_assertion_error__',
                    '__request_custom_exception__',
                ]:
                    exception = ctx.get(e)
                    if exception:
                        code = exception.get('code')
                        msg = exception.get('msg')
                        log.error(f'Request exception: {msg}')
                        break
            except Exception as e:
                elapsed = round((time.perf_counter() - ctx.perf_time) * 1000, 3)
                code = getattr(e, 'code', StandardResponseCode.HTTP_500)  # Compatible with SQLAlchemy exception usage
                msg = getattr(e, 'msg', str(e))  # It is not recommended to use the traceback module to obtain error information, as code information will be exposed.
                status = StatusType.disable
                error = e
                log.error(f'Request exception: {e!s}')

            # This information can only be obtained after request
            route = request.scope.get('route')
            summary = route.summary or '' if route else ''

            try:
                # This information comes from JWT certification middleware
                username = request.user.username
            except AttributeError:
                username = None

            # Logging
            log.debug(f'interface summary: [{summary}]')
            log.debug(f'request address: [{ctx.ip}]')
            log.debug(f'request parameter: {args}')
            log.info(f'{request.client.host: <15} | {request.method: <8} | {code!s: <6} | {path} | {elapsed:.3f}ms')
            if request.method != 'OPTIONS':
                log.debug('<-- Request ends')

            # Log creation
            opera_log_in = CreateOperaLogParam(
                trace_id=get_request_trace_id(),
                username=username,
                method=method,
                title=summary,
                path=path,
                ip=ctx.ip,
                country=ctx.country,
                region=ctx.region,
                city=ctx.city,
                user_agent=ctx.user_agent,
                os=ctx.os,
                browser=ctx.browser,
                device=ctx.device,
                args=args,
                status=status,
                code=str(code),
                msg=msg,
                cost_time=elapsed,  # There may be a slight difference from the log (negligible)
                opera_time=ctx.start_time,
            )
            await self.opera_log_queue.put(opera_log_in)

            # Error thrown
            if error:
                raise error from None

        return response

    async def get_request_args(self, request: Request) -> dict[str, Any] | None:
        """
        Get request parameters

        :param request: FastAPI request object
        :return:
        """
        args = {}

        # Query parameters
        query_params = dict(request.query_params)
        if query_params:
            args['query_params'] = await self.desensitization(query_params)

        # Path parameters
        path_params = request.path_params
        if path_params:
            args['path_params'] = await self.desensitization(path_params)

        # Tip: .body() must be obtained before .form()
        # https://github.com/encode/starlette/discussions/1933
        content_type = request.headers.get('Content-Type', '').split(';')

        # Request body
        body_data = await request.body()
        if body_data:
            # Note: Non-json data uses data as key by default
            if 'application/json' not in content_type:
                args['data'] = str(body_data)
            else:
                json_data = await request.json()
                if isinstance(json_data, dict):
                    args['json'] = await self.desensitization(json_data)
                else:
                    args['data'] = str(body_data)

        # Form Parameters
        form_data = await request.form()
        if len(form_data) > 0:
            for k, v in form_data.items():
                form_data = {k: v.filename} if isinstance(v, UploadFile) else {k: v}
            if 'multipart/form-data' not in content_type:
                args['x-www-form-urlencoded'] = await self.desensitization(form_data)
            else:
                args['form-data'] = await self.desensitization(form_data)

        return args or None

    @staticmethod
    @sync_to_async
    def desensitization(args: dict[str, Any]) -> dict[str, Any]:
        """
        Desensitization treatment

        :param args: Parameter dictionary that requires desensitization
        :return:
        """
        for key, value in args.items():
            if key in settings.OPERA_LOG_ENCRYPT_KEY_INCLUDE:
                match settings.OPERA_LOG_ENCRYPT_TYPE:
                    case OperaLogCipherType.aes:
                        args[key] = (AESCipher(settings.OPERA_LOG_ENCRYPT_SECRET_KEY).encrypt(value)).hex()
                    case OperaLogCipherType.md5:
                        args[key] = Md5Cipher.encrypt(value)
                    case OperaLogCipherType.itsdangerous:
                        args[key] = ItsDCipher(settings.OPERA_LOG_ENCRYPT_SECRET_KEY).encrypt(value)
                    case OperaLogCipherType.plan:
                        pass
                    case _:
                        args[key] = '******'

        return args

    @classmethod
    async def consumer(cls) -> None:
        """Operation log consumer"""
        while True:
            logs = await batch_dequeue(
                cls.opera_log_queue,
                max_items=settings.OPERA_LOG_QUEUE_BATCH_CONSUME_SIZE,
                timeout=settings.OPERA_LOG_QUEUE_TIMEOUT,
            )
            if logs:
                try:
                    if settings.DATABASE_ECHO:
                        log.info('Automatically execute [Operation log batch creation] task...')
                    async with async_db_session.begin() as db:
                        await opera_log_service.bulk_create(db=db, objs=logs)
                finally:
                    if not cls.opera_log_queue.empty():
                        cls.opera_log_queue.task_done()
