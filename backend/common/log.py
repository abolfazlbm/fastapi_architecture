#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import inspect
import logging
import os
import re
import sys

from asgi_correlation_id import correlation_id
from loguru import logger

from backend.core.conf import settings
from backend.core.path_conf import LOG_DIR
from backend.utils.timezone import timezone


class InterceptHandler(logging.Handler):
    """
    Log interceptor processor for redirecting the logs of the standard library to loguru

    Reference: https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord):
        # Get the corresponding Loguru level (if present)
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find the caller who logs the log message
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def default_formatter(record):
    """Default log formatter"""

    # Rewrite sqlalchemy echo output
    # https://github.com/sqlalchemy/sqlalchemy/discussions/12791
    record_name = record['name'] or ''
    if record_name.startswith('sqlalchemy'):
        record['message'] = re.sub(r'\s+', ' ', record['message']).strip()

    return settings.LOG_FORMAT if settings.LOG_FORMAT.endswith('\n') else f'{settings.LOG_FORMAT}\n'


def setup_logging() -> None:
    """
    Setting up the log processor

    refer to:
    - https://github.com/benoitc/gunicorn/issues/1572#issuecomment-638391953
    - https://github.com/pawamoy/pawamoy.github.io/issues/17
    """
    # Set root log processor and level
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(settings.LOG_STD_LEVEL)

    for name in logging.root.manager.loggerDict.keys():
        # Clear all default log processors
        logging.getLogger(name).handlers = []

        # Configure log propagation rules
        if 'uvicorn.access' in name or 'watchfiles.main' in name:
            logging.getLogger(name).propagate = False
        else:
            logging.getLogger(name).propagate = True

        # Debug log handlers
        # logging.debug(f'{logging.getLogger(name)}, {logging.getLogger(name).propagate}')

   # Remove the loguru default processor
    logger.remove()

    # correlation_id filter
    # https://github.com/snok/asgi-correlation-id/issues/7
    def correlation_id_filter(record):
        cid = correlation_id.get(settings.TRACE_ID_LOG_DEFAULT_VALUE)
        record['correlation_id'] = cid[: settings.TRACE_ID_LOG_LENGTH]
        return record

    # Configure the loguru processor
    logger.configure(
        handlers=[
            {
                'sink': sys.stdout,
                'level': settings.LOG_STD_LEVEL,
                'format': default_formatter,
                'filter': lambda record: correlation_id_filter(record),
            }
        ]
    )


def set_custom_logfile() -> None:
    """Set custom log files"""
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)

    # Log File
    log_access_file = os.path.join(LOG_DIR, settings.LOG_ACCESS_FILENAME)
    log_error_file = os.path.join(LOG_DIR, settings.LOG_ERROR_FILENAME)

    # Log compression callback
    def compression(filepath):
        filename = filepath.split(os.sep)[-1]
        original_filename = filename.split('.')[0]
        if '-' in original_filename:
            return os.path.join(LOG_DIR, f'{original_filename}.log')
        return os.path.join(LOG_DIR, f'{original_filename}_{timezone.now().strftime("%Y-%m-%d")}.log')

    # General configuration of log files
    # https://loguru.readthedocs.io/en/stable/api/logger.html#loguru._logger.Logger.add
    log_config = {
        'format': default_formatter,
        'enqueue': True,
        'rotation': '00:00',
        'retention': '7 days',
        'compression': lambda filepath: os.rename(filepath, compression(filepath)),
    }

    # Standard output file
    logger.add(
        str(log_access_file),
        level=settings.LOG_FILE_ACCESS_LEVEL,
        filter=lambda record: record['level'].no <= 25,
        backtrace=False,
        diagnose=False,
        **log_config,
    )

    # Standard Error File
    logger.add(
        str(log_error_file),
        level=settings.LOG_FILE_ERROR_LEVEL,
        filter=lambda record: record['level'].no >= 30,
        backtrace=True,
        diagnose=True,
        **log_config,
    )


# Create a logger instance
log = logger
