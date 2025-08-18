#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from backend.common.socketio.server import sio


async def task_notification(msg: str):
    """
    Task notification

    :param msg: Notification information
    :return:
    """
    await sio.emit('task_notification', {'msg': msg})
