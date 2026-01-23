from math import ceil

from fastapi import Request, Response

from backend.common.exception import errors
from backend.common.response.response_code import StandardResponseCode


async def http_limit_callback(request: Request, response: Response, expire: int) -> None:  # noqa: RUF029
    """
    Default callback function when requesting limits

    :param request: FastAPI request object
    :param response: FastAPI response object
    :param expire: remaining milliseconds
    :return:
    """
    expires = ceil(expire / 1000)
    raise errors.HTTPError(
        code=StandardResponseCode.HTTP_429,
        msg='The request is too frequent, please try again later.',
        headers={'Retry-After': str(expires)},
    )
