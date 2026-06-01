import asyncio
import time

from asyncio import Queue
from collections.abc import Awaitable, Callable
from typing import TypeVar

from backend.common.log import log
from backend.common.observability.prometheus.queue import (
    inc_queue_exception,
    observe_batch_dequeue_cost,
    observe_queue_size,
)

T = TypeVar('T')


async def batch_dequeue(queue: Queue[T], max_items: int, timeout: float, *, queue_name: str = 'default') -> list[T]:
    """
    Get multiple items from an asynchronous queue

    :param queue: `asyncio.Queue` queue for getting items
    :param max_items: The maximum number of items to get from the queue
    :param timeout: Total wait timeout (seconds)
    :param queue_name: Queue name, used for Prometheus tags
    :return:
    """
    items = []
    start = time.perf_counter()

    async def collector() -> None:
        while len(items) < max_items:
            item = await queue.get()
            items.append(item)
            observe_queue_size(queue, queue_name=queue_name)

    try:
        await asyncio.wait_for(collector(), timeout=timeout)
    except asyncio.TimeoutError:
        pass
    except Exception as e:
        inc_queue_exception(queue_name=queue_name)
        log.error(f'Queue batch acquisition failed: {e}')
    finally:
        observe_batch_dequeue_cost(start, queue_name=queue_name)
        observe_queue_size(queue, queue_name=queue_name)

    return items


async def batch_consume(
    queue: Queue[T],
    max_items: int,
    timeout: float,
    handler: Callable[..., Awaitable[None]],
    *,
    queue_name: str = 'default',
    error_message: str = 'Queue batch processing failed',
    item_name: str = 'Data',
) -> None:
    """
    Continuous batch consumption queue

    :param queue: `asyncio.Queue` queue for getting items
    :param max_items: The maximum number of items to get from the queue
    :param timeout: Total wait timeout (seconds)
    :param handler: batch processing function
    :param queue_name: Queue name, used for Prometheus tags
    :param error_message: Processing failure log message
    :param item_name: Queue data name
    :return:
    """
    while True:
        items = await batch_dequeue(queue, max_items=max_items, timeout=timeout, queue_name=queue_name)
        if not items:
            continue

        try:
            await handler(items)
        except Exception as e:
            log.error(f'{error_message}，lost {len(items)} item {item_name}: {e}')
        finally:
            for _ in items:
                queue.task_done()
                observe_queue_size(queue, queue_name=queue_name)
