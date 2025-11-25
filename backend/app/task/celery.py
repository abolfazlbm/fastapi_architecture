import os

import celery
import celery_aio_pool

from backend.app.task.tasks.beat import LOCAL_BEAT_SCHEDULE
from backend.core.conf import settings
from backend.core.path_conf import BASE_PATH


def find_task_packages() -> list[str]:
    packages = []
    task_dir = BASE_PATH / 'app' / 'task' / 'tasks'
    for root, _dirs, files in os.walk(task_dir):
        if 'tasks.py' in files:
            package = root.replace(str(BASE_PATH.parent) + os.path.sep, '').replace(os.path.sep, '.')
            packages.append(package)
    return packages


def init_celery() -> celery.Celery:
    """Initialize the Celery application"""

    # TODO: Update this work if celery version >= 6.0.0
    # https://github.com/fastapi-practices/fastapi_best_architecture/issues/321
    # https://github.com/celery/celery/issues/7874
    celery.app.trace.build_tracer = celery_aio_pool.build_async_tracer
    celery.app.trace.reset_worker_optimizations()

    broker_url = f'amqp://{settings.CELERY_RABBITMQ_USERNAME}:{settings.CELERY_RABBITMQ_PASSWORD}@{settings.CELERY_RABBITMQ_HOST}:{settings.CELERY_RABBITMQ_PORT}/{settings.CELERY_RABBITMQ_VHOST}'
    if settings.CELERY_BROKER == 'redis':
        broker_url = f'redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.CELERY_BROKER_REDIS_DATABASE}'

    result_backend = f'db+postgresql+psycopg://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_SCHEMA}'
    if settings.DATABASE_TYPE == 'mysql':
        result_backend = result_backend.replace('postgresql+psycopg', 'mysql+pymysql')

    # https://docs.celeryq.dev/en/stable/userguide/configuration.html
    app = celery.Celery(
        'fba_celery',
        broker_url=broker_url,
        broker_connection_retry_on_startup=True,
        result_backend=result_backend,
        result_extended=True,
        database_engine_options={'echo': settings.DATABASE_ECHO},
        # result_expires=0, # Clean up the task results, default to 4 a.m., 0 or None means no cleaning
        # beat_sync_every=1, # Save task status cycle, default 3 * 60 seconds
        beat_schedule=LOCAL_BEAT_SCHEDULE,
        beat_scheduler='backend.app.task.utils.schedulers:DatabaseScheduler',
        task_cls='backend.app.task.tasks.base:TaskBase',
        task_track_started=True,
        enable_utc=False,
        timezone=settings.DATETIME_TIMEZONE,
    )

    # 在 Celery Setting this parameter in is invalid
    # 参数：https://github.com/celery/celery/issues/7270
    app.loader.override_backends = {'db': 'backend.app.task.database:DatabaseBackend'}

    # Automatically discover tasks
    packages = find_task_packages()
    app.autodiscover_tasks(packages)

    return app


# Create a Celery instance
celery_app: celery.Celery = init_celery()
