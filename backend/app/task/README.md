## Task Introduction

Current task uses Celery
Implementation, please check [#225](https://github.com/fastapi-practices/fastapi_best_architecture/discussions/225)

## Timing Tasks

Write relevant timing tasks in the `backend/app/task/tasks/beat.py` file

### Simple Task

Write relevant task code in the `backend/app/task/tasks/tasks.py` file

### Hierarchy Tasks

If you want to divide the task into a directory level to make the task structure clearer, you can create any new directory, but you must pay attention to it

1. Create a new python package directory under the `backend/app/task/tasks` directory
2. After creating a new directory, be sure to update `CELERY_TASKS_PACKAGES` in the `conf.py` configuration and add the path to the new directory module to this list.
3. In the new directory, be sure to add the `tasks.py` file and write the relevant task code in this file.

## Message Proxy

You can control message broker selection via `CELERY_BROKER`, which supports redis and rabbitmq

For local debugging, redis is recommended

For online environments, use rabbitmq for forced use
