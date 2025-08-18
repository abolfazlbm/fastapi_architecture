#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from celery import schedules
from celery.schedules import ParseException, crontab_parser

from backend.common.exception import errors
from backend.utils.timezone import timezone


class TzAwareCrontab(schedules.crontab):
    """Time zone awareness Crontab"""

    def __init__(self, minute='*', hour='*', day_of_week='*', day_of_month='*', month_of_year='*', app=None):
        super().__init__(
            minute=minute,
            hour=hour,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            month_of_year=month_of_year,
            nowfun=timezone.now,
            app=app,
        )

    def is_due(self, last_run_at: datetime) -> tuple[bool, int | float]:
        """
        Task expiration status

        :param last_run_at: last run time
        :return:
        """
        rem_delta = self.remaining_estimate(last_run_at)
        rem = max(rem_delta.total_seconds(), 0)
        due = rem == 0
        if due:
            rem_delta = self.remaining_estimate(self.now())
            rem = max(rem_delta.total_seconds(), 0)
        return schedules.schedstate(is_due=due, next=rem)

    def __reduce__(self) -> tuple[type, tuple[str, str, str, str, str], None]:
        return (
            self.__class__,
            (
                self._orig_minute,
                self._orig_hour,
                self._orig_day_of_week,
                self._orig_day_of_month,
                self._orig_month_of_year,
            ),
            None,
        )


def crontab_verify(crontab: str) -> None:
    """
    Verify Celery crontab expressions

    :param crontab: Plan expression
    :return:
    """
    crontab_split = crontab.split(' ')
    if len(crontab_split) != 5:
        raise errors.RequestError(msg='Crontab expression is illegal')

    try:
        crontab_parser(60, 0).parse(crontab_split[0])  # minute
        crontab_parser(24, 0).parse(crontab_split[1])  # hour
        crontab_parser(7, 0).parse(crontab_split[2])  # day_of_week
        crontab_parser(31, 1).parse(crontab_split[3])  # day_of_month
        crontab_parser(12, 1).parse(crontab_split[4])  # month_of_year
    except ParseException:
        raise errors.RequestError(msg='Crontab expression is illegal')
