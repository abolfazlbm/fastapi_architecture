from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import anyio

from backend.core.path_conf import RELOAD_LOCK_FILE
from backend.database.redis import redis_client


@asynccontextmanager
async def acquire_distributed_reload_lock() -> AsyncGenerator[None, Any]:
    """Get distributed hot reload lock"""
    lock = redis_client.lock(
        'fba:reload_lock',
        timeout=300, # Lock timeout: 5 minutes
        blocking_timeout=60, # Timeout for acquiring lock waiting: 60 seconds
    )
    await lock.acquire()

    # File lock (notifies the file monitor to skip reloading)
    lock_path = anyio.Path(RELOAD_LOCK_FILE)
    await lock_path.touch()

    try:
        yield
    finally:
        await lock_path.unlink(missing_ok=True)
        if await lock.owned():
            await lock.release()
