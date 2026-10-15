## Task Introduction

Current task uses Celery
Implementation, please check [#225](https://github.com/fastapi-practices/fastapi-best-architecture/discussions/225)

## Timing Tasks

Write relevant timing tasks in the `backend/app/task/tasks/beat.py` file

### Simple Task

Write relevant task code in the `backend/app/task/tasks/tasks.py` file

### Hierarchy Tasks

If you want to divide the task into a directory level to make the task structure clearer, you can create any new directory, but you must pay attention to it

1. Create a new python package directory under the `backend/app/task/tasks` directory
2. In the new directory, be sure to add the `tasks.py` file and write the relevant task code in this file

## Message Proxy

You can control message broker selection via `CELERY_BROKER`, which supports redis and rabbitmq

For local debugging, redis is recommended

For online environments, use rabbitmq for forced use

## Flower 只读监控

`fba celery flower` 默认启用只读模式，允许查看 worker 和任务，禁止撤销任务、调整进程池、关闭 worker 等管理操作。Supervisor 部署也显式启用只读模式。

需要管理操作时，使用 `fba celery flower --no-read-only`。部署方式可将 `fba_celery_flower.conf` 中的 `--read-only=True` 改为 `--read-only=False`。

Flower 2.2 对跨站写请求进行校验，反向代理应保留正确的 Host；同源 Basic Auth 页面无需额外的 cookie XSRF token。
