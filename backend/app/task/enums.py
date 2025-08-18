#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from backend.common.enums import IntEnum, StrEnum


class TaskSchedulerType(IntEnum):
    """Task Scheduling Type"""

    INTERVAL = 0
    CRONTAB = 1


class PeriodType(StrEnum):
    """Cycle type"""

    DAYS = 'days'
    HOURS = 'hours'
    MINUTES = 'minutes'
    SECONDS = 'seconds'
    MICROSECONDS = 'microseconds'
