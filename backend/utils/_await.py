import asyncio
import atexit
import threading
import weakref

from functools import wraps
from typing import Any, Awaitable, Callable, Coroutine, TypeVar

T = TypeVar('T')


class _TaskRunner:
    """Task runner that runs asyncio event loop on background thread"""

    def __init__(self):
        self.__loop: asyncio.AbstractEventLoop | None = None
        self.__thread: threading.Thread | None = None
        self.__lock = threading.Lock()
        atexit.register(self.close)

    def close(self):
        """Close the event loop and clean up"""
        if self.__loop:
            self.__loop.stop()
            self.__loop = None
        if self.__thread:
            self.__thread.join()
            self.__thread = None
        name = f'TaskRunner-{threading.get_ident()}'
        _runner_map.pop(name, None)

    def _target(self):
        """Objective function of background thread"""
        try:
            self.__loop.run_forever()
        finally:
            self.__loop.close()

    def run(self, coro: Awaitable[T]) -> T:
        """Run the coroutine on the background event loop and return its result"""
        with self.__lock:
            name = f'TaskRunner-{threading.get_ident()}'
            if self.__loop is None:
                self.__loop = asyncio.new_event_loop()
                self.__thread = threading.Thread(target=self._target, daemon=True, name=name)
                self.__thread.start()
            future = asyncio.run_coroutine_threadsafe(coro, self.__loop)
            return future.result()


_runner_map = weakref.WeakValueDictionary()


def run_await(coro: Callable[..., Awaitable[T]] | Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., T]:
    """Wrap the coroutine in a function that will run on the background event loop until it is executed"""

    @wraps(coro)
    def wrapped(*args, **kwargs):
        inner = coro(*args, **kwargs)
        if not asyncio.iscoroutine(inner) and not asyncio.isfuture(inner):
            raise TypeError(f'Expected coroutine, got {type(inner)}')
        try:
           # If the event loop is running, use task calls
            asyncio.get_running_loop()
            name = f'TaskRunner-{threading.get_ident()}'
            if name not in _runner_map:
                _runner_map[name] = _TaskRunner()
            return _runner_map[name].run(inner)
        except RuntimeError:
            # If not, create a new event loop
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(inner)

    wrapped.__doc__ = coro.__doc__
    return wrapped
