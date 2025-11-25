from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.common.i18n import i18n


def get_current_language(request: Request) -> str | None:
    """
    Get the language preference for the current request

    :param request: FastAPI request object
    :return:
    """
    accept_language = request.headers.get('Accept-Language', '')
    if not accept_language:
        return None

    languages = [lang.split(';')[0] for lang in accept_language.split(',')]
    lang = languages[0].lower().strip()

    # Language Mapping
    lang_mapping = {
        'zh': 'zh-CN',
        'zh-cn': 'zh-CN',
        'zh-hans': 'zh-CN',
        'en': 'en-US',
        'en-us': 'en-US',
    }

    return lang_mapping.get(lang, lang)


class I18nMiddleware(BaseHTTPMiddleware):
    """International middleware"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Handle requests and set internationalization languages

        :param request: FastAPI request object
        :param call_next: next middleware or route processing function
        :return:
        """
        language = get_current_language(request)

        # Set international language
        if language and i18n.current_language != language:
            i18n.current_language = language

        response = await call_next(request)

        return response
