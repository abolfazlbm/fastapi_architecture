import asyncio

from asyncio import Queue

from backend.common.log import log


async def batch_dequeue(queue: Queue, max_items: int, timeout: float) -> list:
    """
    Get multiple items from an asynchronous queue

    :param queue: `asyncio.Queue` queue used to get the project
    :param max_items: Maximum number of items obtained from the queue
    :param timeout: Total waiting timeout (seconds)
    :return:
    """
    items = []

    async def collector() -> None:
        while len(items) < max_items:
            item = await queue.get()
            items.append(item)

    try:
        await asyncio.wait_for(collector(), timeout=timeout)
    except asyncio.TimeoutError:
        pass
    except Exception as e:
        log.error(f'Queue batch acquisition failed: {e}')

    return items
