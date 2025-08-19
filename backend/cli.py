#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import subprocess

from dataclasses import dataclass
from typing import Annotated, Literal

import cappa
import granian

from rich.panel import Panel
from rich.text import Text
from sqlalchemy import text
from watchfiles import PythonFilter

from backend import console, get_version
from backend.common.enums import DataBaseType, PrimaryKeyType
from backend.common.exception.errors import BaseExceptionMixin
from backend.core.conf import settings
from backend.database.db import async_db_session
from backend.plugin.tools import get_plugin_sql
from backend.utils.file_ops import install_git_plugin, install_zip_plugin, parse_sql_script


class CustomReloadFilter(PythonFilter):
    """Custom overload filter"""

    def __init__(self):
        super().__init__(extra_extensions=['.json', '.yaml', '.yml'])


def run(host: str, port: int, reload: bool, workers: int | None) -> None:
    url = f'http://{host}:{port}'
    docs_url = url + settings.FASTAPI_DOCS_URL
    redoc_url = url + settings.FASTAPI_REDOC_URL
    openapi_url = url + settings.FASTAPI_OPENAPI_URL

    panel_content = Text()
    panel_content.append(f'📝 Swagger Documentation: {docs_url}\n', style='blue')
    panel_content.append(f'📚 Redoc Documentation: {redoc_url}\n', style='yellow')
    panel_content.append(f'📡 OpenAPI JSON: {openapi_url}\n', style='green')
    panel_content.append(
        '🌍 official document: ...',
        style='cyan',
    )

    console.print(Panel(panel_content, title='fba service information', border_style='purple', padding=(1, 2)))
    granian.Granian(
        target='backend.main:app',
        interface='asgi',
        address=host,
        port=port,
        reload=not reload,
        reload_filter=CustomReloadFilter,
        workers=workers or 1,
    ).serve()


def run_celery_worker(log_level: Literal['info', 'debug']) -> None:
    try:
        subprocess.run(['celery', '-A', 'backend.app.task.celery', 'worker', '-l', f'{log_level}', '-P', 'gevent'])
    except KeyboardInterrupt:
        pass


def run_celery_beat(log_level: Literal['info', 'debug']) -> None:
    try:
        subprocess.run(['celery', '-A', 'backend.app.task.celery', 'beat', '-l', f'{log_level}'])
    except KeyboardInterrupt:
        pass


def run_celery_flower(port: int, basic_auth: str) -> None:
    try:
        subprocess.run([
            'celery',
            '-A',
            'backend.app.task.celery',
            'flower',
            f'--port={port}',
            f'--basic-auth={basic_auth}',
        ])
    except KeyboardInterrupt:
        pass


async def install_plugin(
    path: str, repo_url: str, no_sql: bool, db_type: DataBaseType, pk_type: PrimaryKeyType
) -> None:
    if not path and not repo_url:
        raise cappa.Exit('path or repo_url must specify one of them', code=1)
    if path and repo_url:
        raise cappa.Exit('path and repo_url cannot be specified at the same time', code=1)

    plugin_name = None
    console.print(Text('Start installing plugin...', style='bold cyan'))

    try:
        if path:
            plugin_name = await install_zip_plugin(file=path)
        if repo_url:
            plugin_name = await install_git_plugin(repo_url=repo_url)

        console.print(Text(f'plugin {plugin_name} installed successfully', style='bold green'))

        sql_file = await get_plugin_sql(plugin_name, db_type, pk_type)
        if sql_file and not no_sql:
            console.print(Text('Start auto-executing plugin SQL scripts...', style='bold cyan'))
            await execute_sql_scripts(sql_file)

    except Exception as e:
        raise cappa.Exit(e.msg if isinstance(e, BaseExceptionMixin) else str(e), code=1)


async def execute_sql_scripts(sql_scripts: str) -> None:
    async with async_db_session.begin() as db:
        try:
            stmts = await parse_sql_script(sql_scripts)
            for stmt in stmts:
                await db.execute(text(stmt))
        except Exception as e:
            raise cappa.Exit(f'SQL Script execution failed：{e}', code=1)

    console.print(Text('The SQL script has been executed', style='bold green'))


@cappa.command(help='Run API Service')
@dataclass
class Run:
    host: Annotated[
        str,
        cappa.Arg(
            long=True,
            default='127.0.0.1',
            help='The host IP address of the service provided, for local development, please use `127.0.0.1`. '
            'To enable public access, for example in a LAN, use `0.0.0.0`',
        ),
    ]
    port: Annotated[
        int,
        cappa.Arg(long=True, default=8000, help='host port number for providing the service'),
    ]
    no_reload: Annotated[
        bool,
        cappa.Arg(long=True, default=False, help='Disable automatic reloading of the server when (code) file changes'),
    ]
    workers: Annotated[
        int | None,
        cappa.Arg(long=True, default=None, help="use multiple worker processes, must be used simultaneously with `--no-reload` "),
    ]

    def __call__(self):
        run(host=self.host, port=self.port, reload=self.no_reload, workers=self.workers)


@cappa.command(help='Start the Celery worker service from the current host')
@dataclass
class Worker:
    log_level: Annotated[
        Literal['info', 'debug'],
        cappa.Arg(long=True, short='-l', default='info', help='Log output level'),
    ]

    def __call__(self):
        run_celery_worker(log_level=self.log_level)


@cappa.command(help='Start the Celery beat service from the current host')
@dataclass
class Beat:
    log_level: Annotated[
        Literal['info', 'debug'],
        cappa.Arg(long=True, short='-l', default='info', help='Log output level'),
    ]

    def __call__(self):
        run_celery_beat(log_level=self.log_level)


@cappa.command(help='Start the Celery flower service from the current host')
@dataclass
class Flower:
    port: Annotated[int, cappa.Arg(long=True, default=8555, help='Host port number that provides the service')]
    basic_auth: Annotated[str, cappa.Arg(long=True, default='admin:123456', help='page login username and password')]

    def __call__(self):
        run_celery_flower(port=self.port, basic_auth=self.basic_auth)


@cappa.command(help='Run the Celery service')
@dataclass
class Celery:
    subcmd: cappa.Subcommands[Worker | Beat | Flower]


@cappa.command(help='Added plug-in')
@dataclass
class Add:
    path: Annotated[
        str | None,
        cappa.Arg(long=True, help='local full path to ZIP plugin'),
    ]
    repo_url: Annotated[
        str | None,
        cappa.Arg(long=True, help="Git plugin' repository address"),
    ]
    no_sql: Annotated[
        bool,
        cappa.Arg(long=True, default=False, help='Disable plugin SQL scripts auto-execution'),
    ]
    db_type: Annotated[
        DataBaseType,
        cappa.Arg(long=True, default='mysql', help='Database type for executing plugin SQL scripts'),
    ]
    pk_type: Annotated[
        PrimaryKeyType,
        cappa.Arg(long=True, default='autoincrement', help='Execute plugin SQL script database primary key type'),
    ]

    async def __call__(self):
        await install_plugin(self.path, self.repo_url, self.no_sql, self.db_type, self.pk_type)


@cappa.command(help='A efficient fba command line interface')
@dataclass
class FbaCli:
    version: Annotated[
        bool,
        cappa.Arg(short='-V', long=True, default=False, show_default=False, help='Print the current version number'),
    ]
    sql: Annotated[
        str,
        cappa.Arg(value_name='PATH', long=True, default='', show_default=False, help='Execute SQL scripts in transaction'),
    ]
    subcmd: cappa.Subcommands[Run | Celery | Add | None] = None

    async def __call__(self):
        if self.version:
            get_version()
        if self.sql:
            await execute_sql_scripts(self.sql)


def main() -> None:
    output = cappa.Output(error_format='[red]Error[/]: {message}\n\nFor more information, try "[cyan]--help[/]"')
    asyncio.run(cappa.invoke_async(FbaCli, output=output))
