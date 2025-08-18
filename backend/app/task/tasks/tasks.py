#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from time import sleep

from anyio import sleep as asleep

from backend.app.task.celery import celery_app


@celery_app.task(name='task_demo')
def task_demo() -> str:
    """Sample task, simulation time-consuming operation"""
    sleep(30)
    return 'test async'


@celery_app.task(name='task_demo_async')
async def task_demo_async() -> str:
    """Async sample task, simulate time-consuming operations"""
    await asleep(30)
    return 'test async'


@celery_app.task(name='task_demo_params')
async def task_demo_params(hello: str, world: str | None = None) -> str:
    """Sample sample task, simulate parameter transfer operation"""
    return hello + world
