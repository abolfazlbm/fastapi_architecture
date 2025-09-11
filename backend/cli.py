#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import subprocess

from dataclasses import dataclass
from typing import Annotated, Literal

import cappa
import granian

from cappa.output import error_format
from rich.panel import Panel
from rich.prompt import IntPrompt
from rich.table import Table
from rich.text import Text
from sqlalchemy import text
from watchfiles import PythonFilter

from backend import __version__
from backend.common.enums import DataBaseType, PrimaryKeyType
from backend.common.exception.errors import BaseExceptionMixin
from backend.core.conf import settings
from backend.database.db import async_db_session
from backend.plugin.code_generator.schema.code import ImportParam
from backend.plugin.code_generator.service.business_service import gen_business_service
from backend.plugin.code_generator.service.code_service import gen_service
from backend.plugin.tools import get_plugin_sql
from backend.utils._await import run_await
from backend.utils.console import console
from backend.utils.file_ops import install_git_plugin, install_zip_plugin, parse_sql_script

output_help = '\nMore information, try "[cyan]--help[/]"'


class CustomReloadFilter(PythonFilter):
    """Custom overload filter"""

    def __init__(self):
        super().__init__(extra_extensions=['.json', '.yaml', '.yml'])


def run(host: str, port: int, reload: bool, workers: int) -> None:
    url = f'http://{host}:{port}'
    docs_url = url + settings.FASTAPI_DOCS_URL
    redoc_url = url + settings.FASTAPI_REDOC_URL
    openapi_url = url + (settings.FASTAPI_OPENAPI_URL or '')

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
        workers=workers,
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


async def import_table(
    app: str,
    table_schema: str,
    table_name: str,
) -> None:
    try:
        obj = ImportParam(app=app, table_schema=table_schema, table_name=table_name)
        await gen_service.import_business_and_model(obj=obj)
    except Exception as e:
        raise cappa.Exit(e.msg if isinstance(e, BaseExceptionMixin) else str(e), code=1)


def generate(gen: bool) -> None:
    if not gen:
        console.print(output_help)
        return

    try:
        ids = []
        results = run_await(gen_business_service.get_all)()

        if not results:
            raise cappa.Exit('[red]No code generation business available! Please import first through the import command！[/]')

        table = Table(show_header=True, header_style='bold magenta')
        table.add_column('Business number', style='cyan', no_wrap=True, justify='center')
        table.add_column('Application name', style='green', no_wrap=True)
        table.add_column('Generate path', style='yellow')
        table.add_column('Remark', style='blue')

        for result in results:
            ids.append(result.id)
            table.add_row(
                str(result.id),
                result.app_name,
                result.gen_path or f'Application {result.app_name} root path',
                result.remark or '',
            )

        console.print(table)
        business = IntPrompt.ask('Please select a business number from', choices=[str(_id) for _id in ids])

        gen_path = run_await(gen_service.generate)(pk=business)
    except Exception as e:
        raise cappa.Exit(e.msg if isinstance(e, BaseExceptionMixin) else str(e), code=1)

    console.print(Text('\nThe code has been generated', style='bold green'))
    console.print(Text('\nPlease check for details：'), Text(gen_path, style='bold magenta'))


@cappa.command(help='Run API Service', default_long=True)
@dataclass
class Run:
    host: Annotated[
        str,
        cappa.Arg(
            default='127.0.0.1',
            help='The host IP address of the service provided, for local development, please use `127.0.0.1`. '
            'To enable public access, for example in a LAN, use `0.0.0.0`',
        ),
    ]
    port: Annotated[
        int,
        cappa.Arg(default=8000, help='The host port number of the service provided'),
    ]
    no_reload: Annotated[
        bool,
        cappa.Arg(default=False, help='Disable automatic reloading of the server when (code) file changes'),
    ]
    workers: Annotated[
        int,
        cappa.Arg(default=1, help='Using multiple worker processes, you must use `--no-reload` Use simultaneously'),
    ]

    def __call__(self):
        run(host=self.host, port=self.port, reload=self.no_reload, workers=self.workers)


@cappa.command(help='Start the Celery worker service from the current host', default_long=True)
@dataclass
class Worker:
    log_level: Annotated[
        Literal['info', 'debug'],
        cappa.Arg(short='-l', default='info', help='Log output level'),
    ]

    def __call__(self):
        run_celery_worker(log_level=self.log_level)


@cappa.command(help='Start the Celery beat service from the current host', default_long=True)
@dataclass
class Beat:
    log_level: Annotated[
        Literal['info', 'debug'],
        cappa.Arg(short='-l', default='info', help='Log output level'),
    ]

    def __call__(self):
        run_celery_beat(log_level=self.log_level)


@cappa.command(help='Start the Celery flower service from the current host', default_long=True)
@dataclass
class Flower:
    port: Annotated[
        int,
        cappa.Arg(default=8555, help='The host port number of the service provided'),
    ]
    basic_auth: Annotated[
        str,
        cappa.Arg(default='admin:123456', help='Username and password for page login'),
    ]

    def __call__(self):
        run_celery_flower(port=self.port, basic_auth=self.basic_auth)


@cappa.command(help='Run the Celery service')
@dataclass
class Celery:
    subcmd: cappa.Subcommands[Worker | Beat | Flower]


@cappa.command(help='Added plug-in', default_long=True)
@dataclass
class Add:
    path: Annotated[
        str | None,
        cappa.Arg(help='local full path to ZIP plugin'),
    ]
    repo_url: Annotated[
        str | None,
        cappa.Arg(help="Git plugin' repository address"),
    ]
    no_sql: Annotated[
        bool,
        cappa.Arg(default=False, help='Disable plugin SQL scripts auto-execution'),
    ]
    db_type: Annotated[
        DataBaseType,
        cappa.Arg(default='mysql', help='Database type for executing plugin SQL scripts'),
    ]
    pk_type: Annotated[
        PrimaryKeyType,
        cappa.Arg(default='autoincrement', help='Execute plugin SQL script database primary key type'),
    ]

    async def __call__(self):
        await install_plugin(self.path, self.repo_url, self.no_sql, self.db_type, self.pk_type)


@cappa.command(help='Import code to generate business and model columns', default_long=True)
@dataclass
class Import:
    app: Annotated[
        str,
        cappa.Arg(help='Application name, used for code generation to specify app'),
    ]
    table_schema: Annotated[
        str,
        cappa.Arg(short='tc', default='fba', help='Database name'),
    ]
    table_name: Annotated[
        str,
        cappa.Arg(short='tn', help='Database table name'),
    ]

    async def __call__(self):
        await import_table(self.app, self.table_schema, self.table_name)


@cappa.command(name='codegen', help='Code generation (experience the complete functions, please deploy the fba vben front-end project yourself)', default_long=True)
@dataclass
class CodeGenerate:
    gen: Annotated[
        bool,
        cappa.Arg(default=False, show_default=False, help='Execute code generation'),
    ]
    subcmd: cappa.Subcommands[Import | None] = None

    def __call__(self):
        generate(self.gen)


@cappa.command(help='一An efficient fba command line interface', default_long=True)
@dataclass
class FbaCli:
    sql: Annotated[
        str,
        cappa.Arg(value_name='PATH', default='', show_default=False, help='Execute SQL scripts in transaction'),
    ]
    subcmd: cappa.Subcommands[Run | Celery | Add | CodeGenerate | None] = None

    async def __call__(self):
        if self.sql:
            await execute_sql_scripts(self.sql)


def main() -> None:
    output = cappa.Output(error_format=f'{error_format}\n{output_help}')
    asyncio.run(cappa.invoke_async(FbaCli, version=__version__, output=output))
