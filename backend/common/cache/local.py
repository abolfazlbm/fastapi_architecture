from typing import Any

import cachebox

from backend.core.conf import settings


class LocalCacheManager:
    """local cache manager"""

    def __init__(self) -> None:
        self.hot_cache: cachebox.TTLCache = cachebox.TTLCache(
            settings.CACHE_LOCAL_MAXSIZE, global_ttl=settings.CACHE_LOCAL_TTL
        )

    def get(self, key: str) -> Any:
        """Get cache"""
        try:
            return self.hot_cache[key]
        except KeyError:
            return None

    def set(self, key: str, value: Any) -> None:
        """Set cache"""
        self.hot_cache[key] = value

    def delete(self, key: str) -> bool:
        """Delete cache"""
        try:
            del self.hot_cache[key]
        except KeyError:
            return False
        return True

    def clear(self) -> None:
        """Clear cache"""
        self.hot_cache.clear()

    def delete_by_prefix(self, key_prefix: str, exclude_keys: str | list[str] | None = None) -> None:
        """
        Delete the cache of the specified prefix

        :param key_prefix: the key prefix to be deleted
        :param exclude_keys: Key or list of keys to exclude
        :return:
        """
        exclude_set = (
            set(exclude_keys)
            if isinstance(exclude_keys, list)
            else {exclude_keys}
            if isinstance(exclude_keys, str)
            else set()
        )
        for key in list(self.hot_cache.keys()):
            if (key == key_prefix or key.startswith(f'{key_prefix}:')) and key not in exclude_set:
                try:
                    del self.hot_cache[key]
                except KeyError:
                    pass


local_cache_manager = LocalCacheManager()
