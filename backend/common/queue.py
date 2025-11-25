import asyncio

from asyncio import Queue


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

    return items
