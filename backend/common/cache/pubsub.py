import asyncio
import json

from backend.common.cache.local import local_cache_manager
from backend.common.log import log
from backend.core.conf import settings
from backend.database.redis import RedisCli, redis_client


class CachePubSubManager:
    """Caching the Pub/Sub Manager"""

    _pubsub_task: asyncio.Task | None = None

    @staticmethod
    async def publish_invalidation(cache_key: str, *, delete_by_prefix: bool) -> None:
        """
        Publish cache failure notifications

        :param cache_key: Cache key
        :param delete_by_prefix: Whether to delete all caches that match the prefix
        :return:
        """
        try:
            message = json.dumps({'cache_key': cache_key, 'delete_by_prefix': delete_by_prefix})
            await redis_client.publish(settings.CACHE_PUBSUB_CHANNEL, message)
        except Exception as e:
            log.warning(f'[CachePubSub] Publishing notifications failed: {e}')

    @staticmethod
    async def subscribe_and_listen() -> None:  # noqa: C901
        """Subscribe and listen to cache failure notifications"""
        reconnect_attempts = 0

        while reconnect_attempts < settings.CACHE_PUBSUB_MAX_RECONNECT_ATTEMPTS:
            pubsub_client: RedisCli | None = None
            pubsub = None

            try:
                # Use a standalone connection
                pubsub_client = RedisCli(socket_timeout=None)
                pubsub = pubsub_client.pubsub()
                await pubsub.subscribe(settings.CACHE_PUBSUB_CHANNEL)

                # Publish the subscription successfully
                reconnect_attempts = 0

                async for message in pubsub.listen():
                    if message['type'] == 'message':
                        try:
                            data = json.loads(message['data'])
                            cache_key = data['cache_key']
                            if not data['delete_by_prefix']:
                                local_cache_manager.delete(cache_key)
                            else:
                                local_cache_manager.delete_by_prefix(cache_key)
                        except json.JSONDecodeError as e:
                            log.warning(f'[CachePubSub] The message is in the wrong format {e}')
                        except Exception as e:
                            log.error(f'[CachePubSub] Notification processing failed: {e}')

            except asyncio.CancelledError:
                break
            except Exception as e:
                reconnect_attempts += 1
                log.error(
                    f'[CachePubSub] Subscription exception ({reconnect_attempts}/{settings.CACHE_PUBSUB_MAX_RECONNECT_ATTEMPTS}): {e}'
                )

                if reconnect_attempts >= settings.CACHE_PUBSUB_MAX_RECONNECT_ATTEMPTS:
                    log.error('[CachePubSub] Reach the maximum number of reconnects and stop the subscription')
                    break

                await asyncio.sleep(settings.CACHE_PUBSUB_RECONNECT_DELAY)
            finally:
                if pubsub_client:
                    try:
                        await pubsub_client.aclose()
                    except Exception:
                        pass
                if pubsub:
                    try:
                        await pubsub.aclose()
                    except Exception:
                        pass

    @classmethod
    def start_listener(cls) -> None:
        """Start the cached Pub/Sub listener"""
        if not settings.CACHE_LOCAL_ENABLED:
            return

        if cls._pubsub_task is None or cls._pubsub_task.done():
            cls._pubsub_task = asyncio.create_task(cls.subscribe_and_listen())

    @classmethod
    async def stop_listener(cls) -> None:
        """Stop caching Pub/Sub listener"""
        if cls._pubsub_task is None:
            return

        if not cls._pubsub_task.done():
            cls._pubsub_task.cancel()
            try:
                await cls._pubsub_task
            except asyncio.CancelledError:
                pass

        cls._pubsub_task = None


cache_pubsub_manager = CachePubSubManager()
