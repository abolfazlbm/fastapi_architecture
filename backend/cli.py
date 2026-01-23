import asyncio
import re
import secrets
import subprocess
import sys

from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Literal

import anyio
import cappa
import granian

from cappa.output import error_format
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table
from rich.text import Text
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession
from watchfiles import PythonFilter

from backend import __version__
from backend.common.enums import DataBaseType, PrimaryKeyType
from backend.common.exception.errors import BaseExceptionError
from backend.common.model import MappedBase
from backend.core.conf import settings
from backend.core.path_conf import (
    ENV_EXAMPLE_FILE_PATH,
    ENV_FILE_PATH,
    MYSQL_SCRIPT_DIR,
    POSTGRESQL_SCRIPT_DIR,
)
from backend.database.db import (
    async_db_session,
    create_database_async_engine,
    create_database_async_session,
    create_database_url,
)
from backend.database.redis import RedisCli, redis_client
from backend.plugin.core import get_plugin_sql, get_plugins
from backend.plugin.installer import install_git_plugin, install_zip_plugin
from backend.utils.console import console
from backend.utils.dynamic_import import import_module_cached
from backend.utils.sql_parser import parse_sql_script

output_help = '\nMore information, try "[cyan]--help[/]"'


class CustomReloadFilter(PythonFilter):
    """Custom overload filter"""

    def __init__(self) -> None:
        super().__init__(extra_extensions=['.json', '.yaml', '.yml'])


def setup_env_file() -> bool:
    if not ENV_EXAMPLE_FILE_PATH.exists():
        console.print('.env.example File does not exist', style='red')
        return False

    try:
        env_content = Path(ENV_EXAMPLE_FILE_PATH).read_text(encoding='utf-8')
        console.print('Configuring database connection information...', style='white')
        db_type = Prompt.ask('database type', choices=['mysql', 'postgresql'], default='postgresql')
        db_host = Prompt.ask('database host', default='127.0.0.1')
        db_port = Prompt.ask('database port', default='5432' if db_type == 'postgresql' else '3306')
        db_user = Prompt.ask('database username', default='postgres' if db_type == 'postgresql' else 'root')
        db_password = Prompt.ask('database password', password=True, default='123456')

        console.print('Configure Redis connection information...', style='white')
        redis_host = Prompt.ask('Redis host', default='127.0.0.1')
        redis_port = Prompt.ask('Redis port', default='6379')
        redis_password = Prompt.ask('Redis password (leave blank to indicate no password)', password=True, default='')
        redis_db = Prompt.ask('Redis database number', default='0')

        console.print('Generate Token key...', style='white')
        token_secret = secrets.token_urlsafe(32)

        console.print('Write to .env file...', style='white')
        env_content = env_content.replace("DATABASE_TYPE='postgresql'", f"DATABASE_TYPE='{db_type}'")
        settings.DATABASE_TYPE = db_type
        env_content = env_content.replace("DATABASE_HOST='127.0.0.1'", f"DATABASE_HOST='{db_host}'")
        settings.DATABASE_HOST = db_host
        env_content = env_content.replace('DATABASE_PORT=5432', f'DATABASE_PORT={db_port}')
        settings.DATABASE_PORT = db_port
        env_content = env_content.replace("DATABASE_USER='postgres'", f"DATABASE_USER='{db_user}'")
        settings.DATABASE_USER = db_user
        env_content = env_content.replace("DATABASE_PASSWORD='123456'", f"DATABASE_PASSWORD='{db_password}'")
        settings.DATABASE_PASSWORD = db_password
        env_content = env_content.replace("REDIS_HOST='127.0.0.1'", f"REDIS_HOST='{redis_host}'")
        settings.REDIS_HOST = redis_host
        env_content = env_content.replace('REDIS_PORT=6379', f'REDIS_PORT={redis_port}')
        settings.REDIS_PORT = redis_port
        env_content = env_content.replace("REDIS_PASSWORD=''", f"REDIS_PASSWORD='{redis_password}'")
        settings.REDIS_PASSWORD = redis_password
        env_content = env_content.replace('REDIS_DATABASE=0', f'REDIS_DATABASE={redis_db}')
        settings.REDIS_DATABASE = redis_db
        env_content = re.sub(r"TOKEN_SECRET_KEY='[^']*'", f"TOKEN_SECRET_KEY='{token_secret}'", env_content)
        settings.TOKEN_SECRET_KEY = token_secret

        Path(ENV_FILE_PATH).write_text(env_content, encoding='utf-8')
        console.print('.env file created successfully', style='green')
    except Exception as e:
        console.print(f'.env file creation failed: {e}', style='red')
        return False
    else:
        return True


async def create_database(conn: AsyncConnection) -> bool:
    try:
        terminate_sql = None
        if DataBaseType.mysql == settings.DATABASE_TYPE:
            check_sql = f"SHOW DATABASES LIKE '{settings.DATABASE_SCHEMA}'"
            drop_sql = f'DROP DATABASE IF EXISTS `{settings.DATABASE_SCHEMA}`'
            create_sql = (
                f'CREATE DATABASE `{settings.DATABASE_SCHEMA}` CHARACTER SET {settings.DATABASE_CHARSET} '
                f'COLLATE {settings.DATABASE_CHARSET}_unicode_ci'
            )
        else:
            check_sql = f"SELECT 1 FROM pg_database WHERE datname = '{settings.DATABASE_SCHEMA}'"
            drop_sql = f'DROP DATABASE IF EXISTS {settings.DATABASE_SCHEMA}'
            create_sql = f'CREATE DATABASE {settings.DATABASE_SCHEMA}'
            terminate_sql = (
                f'SELECT pg_terminate_backend(pid) FROM pg_stat_activity '
                f"WHERE datname = '{settings.DATABASE_SCHEMA}' AND pid <> pg_backend_pid()"
            )

        result = await conn.execute(text(check_sql))
        exists = result.fetchone() is not None
        console.print(f'Rebuild {settings.DATABASE_SCHEMA} database...', style='white')
        if exists:
            if terminate_sql:
                await conn.execute(text(terminate_sql))
            await conn.execute(text(drop_sql))
        await conn.execute(text(create_sql))
        console.print('Database created successfully', style='green')
    except Exception as e:
        console.print(f'Database creation failed: {e}', style='red')
        return False
    else:
        return True


async def auto_init() -> None:
    """Automated initialization process"""
    console.print('\n[bold cyan]Step 1/3:[/] Configure environment variables', style='bold')
    panel_content = Text()
    panel_content.append('[Environment variable configuration]', style='bold green')
    panel_content.append('\n\n • Database connection information')
    panel_content.append('\n • Redis connection information')
    panel_content.append('\n • Token key (automatically generated)')

    console.print(Panel(panel_content, title=f'fba (v{__version__}) - environment variable', border_style='cyan', padding=(1, 2)))
    if not setup_env_file():
        raise cappa.Exit('.env file configuration failed', code=1)

    console.print('\n[bold cyan]Step 2/3:[/] Database creation', style='bold')
    panel_content = Text()
    panel_content.append('[Database Configuration]', style='bold green')
    panel_content.append('\n\n • Type: ')
    panel_content.append(f'{settings.DATABASE_TYPE}', style='yellow')
    panel_content.append('\n • Host: ')
    panel_content.append(f'{settings.DATABASE_HOST}:{settings.DATABASE_PORT}', style='yellow')
    panel_content.append('\n • Database: ')
    panel_content.append(f'{settings.DATABASE_SCHEMA}', style='yellow')
    panel_content.append('\n • Primary key mode: ')
    panel_content.append(f'{settings.DATABASE_PK_MODE}', style='yellow')

    console.print(Panel(panel_content, title=f'fba (v{__version__}) - database', border_style='cyan', padding=(1, 2)))
    ok = Prompt.ask('The database will be created/rebuilt soon[red][/red], are you sure to continue?', choices=['y', 'n'], default='n')

    if ok.lower() == 'y':
        async_init_engine = create_database_async_engine(create_database_url(with_database=False))
        async with async_init_engine.connect() as conn:
            await conn.execution_options(isolation_level='AUTOCOMMIT')
            if not await create_database(conn):
                raise cappa.Exit('Database creation failed', code=1)
    else:
        console.print('Database operation canceled', style='yellow')

    console.print('\n[bold cyan]Step 3/3:[/] Initialize database tables and data', style='bold')
    async_init_engine = create_database_async_engine(create_database_url())
    async_init_db_session = create_database_async_session(async_init_engine)
    redis_init_client = RedisCli(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DATABASE,
    )
    await redis_init_client.init()
    async with async_init_db_session.begin() as db:
        await init(db, redis_init_client)


async def init(db: AsyncSession, redis: RedisCli) -> None:
    panel_content = Text()
    panel_content.append('【Database configuration】', style='bold green')
    panel_content.append('\n\n  • type: ')
    panel_content.append(f'{settings.DATABASE_TYPE}', style='yellow')
    panel_content.append('\n  • host：')
    panel_content.append(f'{settings.DATABASE_HOST}:{settings.DATABASE_PORT}', style='yellow')
    panel_content.append('\n  • database：')
    panel_content.append(f'{settings.DATABASE_SCHEMA}', style='yellow')
    panel_content.append('\n  • primaryKeyMode：')
    panel_content.append(f'{settings.DATABASE_PK_MODE}', style='yellow')
    pk_details = panel_content.from_markup(
        '[link=https://fastapi-practices.github.io/fastapi_best_architecture_docs/backend/reference/pk.html]（LearnMore）[/]'
    )
    panel_content.append(pk_details)
    panel_content.append('\n\n【Redis deploy】', style='bold green')
    panel_content.append('\n\n  • host：')
    panel_content.append(f'{settings.REDIS_HOST}:{settings.REDIS_PORT}', style='yellow')
    panel_content.append('\n  • database：')
    panel_content.append(f'{settings.REDIS_DATABASE}', style='yellow')
    plugins = get_plugins()
    panel_content.append('\n\n【Plugin Installed】', style='bold green')
    panel_content.append('\n\n  • ')
    if plugins:
        panel_content.append(f'{", ".join(plugins)}', style='yellow')
    else:
        panel_content.append('no', style='dim')

    console.print(Panel(panel_content, title=f'fba (v{__version__}) - initialize', border_style='cyan', padding=(1, 2)))
    ok = Prompt.ask(
        'We are about to [red]create/rebuild database tables[/red] and [red]execute all database scripts[/red]. Are you sure to continue? ', choices=['y', 'n'], default='n'
    )

    if ok.lower() == 'y':
        console.print('Start initialization...', style='white')
        try:
            console.print('Clear Redis cache', style='white')
            for prefix in [
                settings.JWT_USER_REDIS_PREFIX,
                settings.TOKEN_EXTRA_INFO_REDIS_PREFIX,
                settings.TOKEN_REDIS_PREFIX,
                settings.TOKEN_REFRESH_REDIS_PREFIX,
            ]:
                await redis.delete_prefix(prefix)

            console.print('Rebuild database table', style='white')
            conn = await db.connection()
            await conn.run_sync(MappedBase.metadata.drop_all)
            await conn.run_sync(MappedBase.metadata.create_all)

            console.print('Execute SQL script', style='white')
            sql_scripts = await get_sql_scripts()
            for sql_script in sql_scripts:
                console.print(f'Executing: {sql_script}', style='white')
                await execute_sql_scripts(db, sql_script, is_init=True)

            console.print('Initialization successful', style='green')
            console.print('\nQuickly try [bold cyan]fba run[/bold cyan] to start the service~')
        except Exception as e:
            raise cappa.Exit(f'Initialization failed: {e}', code=1)
    else:
        console.print('Initialization operation canceled', style='yellow')


def run(host: str, port: int, reload: bool, workers: int) -> None:  # noqa: FBT001
    url = f'http://{host}:{port}'
    docs_url = url + settings.FASTAPI_DOCS_URL
    redoc_url = url + settings.FASTAPI_REDOC_URL
    openapi_url = url + (settings.FASTAPI_OPENAPI_URL or '')

    panel_content = Text()
    panel_content.append('Python version：', style='bold cyan')
    panel_content.append(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}', style='white')

    panel_content.append('\nAPI RequestAddress: ', style='bold cyan')
    panel_content.append(f'{url}{settings.FASTAPI_API_V1_PATH}', style='blue')

    panel_content.append('\n\nambient mode：', style='bold green')
    env_style = 'yellow' if settings.ENVIRONMENT == 'dev' else 'green'
    panel_content.append(f'{settings.ENVIRONMENT.upper()}', style=env_style)

    plugins = get_plugins()
    panel_content.append('\nPlugin installed：', style='bold green')
    if plugins:
        panel_content.append(f'{", ".join(plugins)}', style='yellow')
    else:
        panel_content.append('No', style='white')

    if settings.ENVIRONMENT == 'dev':
        panel_content.append(f'\n\n📖 Swagger Document: {docs_url}', style='bold magenta')
        panel_content.append(f'\n📚 Redoc   Document: {redoc_url}', style='bold magenta')
        panel_content.append(f'\n📡 OpenAPI JSON: {openapi_url}', style='bold magenta')

    panel_content.append('\n🌐 Architecture official documentation: ', style='bold magenta')
    panel_content.append('#')

    console.print(Panel(panel_content, title=f'fba (v{__version__})', border_style='purple', padding=(1, 2)))
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
    path: str,
    repo_url: str,
    no_sql: bool,  # noqa: FBT001
    db_type: DataBaseType,
    pk_type: PrimaryKeyType,
) -> None:
    if not path and not repo_url:
        raise cappa.Exit('path or repo_url must specify one of them', code=1)
    if path and repo_url:
        raise cappa.Exit('path and repo_url cannot be specified at the same time', code=1)

    plugin_name = None
    console.print('Start installing plugin...', style='bold cyan')

    try:
        if path:
            plugin_name = await install_zip_plugin(file=path)
        if repo_url:
            plugin_name = await install_git_plugin(repo_url=repo_url)

        console.print(f'plugin {plugin_name} installed successfully', style='bold green')

        sql_file = await get_plugin_sql(plugin_name, db_type, pk_type)
        if sql_file and not no_sql:
            console.print('Start auto-executing plugin SQL scripts...', style='bold cyan')
            async with async_db_session.begin() as db:
                await execute_sql_scripts(db, sql_file)

    except Exception as e:
        raise cappa.Exit(e.msg if isinstance(e, BaseExceptionError) else str(e), code=1)


async def get_sql_scripts() -> list[str]:
    sql_scripts = []
    db_script_dir = MYSQL_SCRIPT_DIR if DataBaseType.mysql == settings.DATABASE_TYPE else POSTGRESQL_SCRIPT_DIR
    main_sql_file = (
        db_script_dir / 'init_test_data.sql'
        if PrimaryKeyType.autoincrement == settings.DATABASE_PK_MODE
        else db_script_dir / 'init_snowflake_test_data.sql'
    )

    main_sql_path = anyio.Path(main_sql_file)
    if await main_sql_path.exists():
        sql_scripts.append(str(main_sql_file))

    plugins = get_plugins()
    for plugin in plugins:
        plugin_sql = await get_plugin_sql(plugin, settings.DATABASE_TYPE, settings.DATABASE_PK_MODE)
        if plugin_sql:
            sql_scripts.append(str(plugin_sql))

    return sql_scripts


async def execute_sql_scripts(db: AsyncSession, sql_scripts: str, *, is_init: bool = False) -> None:
    try:
        stmts = await parse_sql_script(sql_scripts)
        for stmt in stmts:
            await db.execute(text(stmt))
    except Exception as e:
        raise cappa.Exit(f'SQL Script execution failed：{e}', code=1)

    if not is_init:
        console.print('The SQL script has been executed', style='bold green')


async def import_table(
    app: str,
    table_schema: str,
    table_name: str,
) -> None:
    from backend.plugin.code_generator.schema.gen import ImportParam
    from backend.plugin.code_generator.service.gen_service import gen_service

    try:
        obj = ImportParam(app=app, table_schema=table_schema, table_name=table_name)
        async with async_db_session.begin() as db:
            await gen_service.import_business_and_model(db=db, obj=obj)
        console.log('Code generation business and model columns are imported successfully', style='bold green')
        console.log('\nTry it quickly [bold cyan]fba codegen[/bold cyan] Generate code~')
    except Exception as e:
        raise cappa.Exit(e.msg if isinstance(e, BaseExceptionError) else str(e), code=1)


async def generate() -> None:
    from backend.plugin.code_generator.service.business_service import gen_business_service
    from backend.plugin.code_generator.service.gen_service import gen_service

    try:
        ids = []
        async with async_db_session() as db:
            results = await gen_business_service.get_all(db=db)

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
        business = IntPrompt.ask('Please select a business number from', choices=[str(id_) for id_ in ids])

        async with async_db_session.begin() as db:
            gen_path = await gen_service.generate(db=db, pk=business)
    except Exception as e:
        raise cappa.Exit(e.msg if isinstance(e, BaseExceptionError) else str(e), code=1)

    console.print('\nThe code has been generated', style='bold green')
    console.print(Text('\nPlease check for details：'), Text(str(gen_path), style='bold magenta'))


@cappa.command(help='Initialize project', default_long=True)
@dataclass
class Init:
    auto: Annotated[
        bool,
        cappa.Arg(default=False, help='Automated initialization mode: automatically create .env, install dependencies, create database and initialize table structure'),
    ]

    async def __call__(self) -> None:
        if self.auto:
            await auto_init()
        else:
            async with async_db_session.begin() as db:
                await init(db, redis_client)


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

    def __call__(self) -> None:
        run(host=self.host, port=self.port, reload=self.no_reload, workers=self.workers)


@cappa.command(help='Start the Celery worker service from the current host', default_long=True)
@dataclass
class Worker:
    log_level: Annotated[
        Literal['info', 'debug'],
        cappa.Arg(short='-l', default='info', help='Log output level'),
    ]

    def __call__(self) -> None:
        run_celery_worker(log_level=self.log_level)


@cappa.command(help='Start the Celery beat service from the current host', default_long=True)
@dataclass
class Beat:
    log_level: Annotated[
        Literal['info', 'debug'],
        cappa.Arg(short='-l', default='info', help='Log output level'),
    ]

    def __call__(self) -> None:
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

    def __call__(self) -> None:
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
        cappa.Arg(default='postgresql', help='Database type for executing plugin SQL scripts'),
    ]
    pk_type: Annotated[
        PrimaryKeyType,
        cappa.Arg(default='autoincrement', help='Execute plugin SQL script database primary key type'),
    ]

    async def __call__(self) -> None:
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

    def __post_init__(self) -> None:
        try:
            import_module_cached('backend.plugin.code_generator')
        except ImportError:
            raise cappa.Exit('The code generation plug-in does not exist, please install this plug-in first')

    async def __call__(self) -> None:
        await import_table(self.app, self.table_schema, self.table_name)


@cappa.command(name='codegen', help='Code generation (experience the complete functions, please deploy the fba vben front-end project yourself)', default_long=True)
@dataclass
class CodeGenerator:
    subcmd: cappa.Subcommands[Import | None] = None

    def __post_init__(self) -> None:
        try:
            import_module_cached('backend.plugin.code_generator')
        except ImportError:
            raise cappa.Exit('The code generation plug-in does not exist, please install this plug-in first')

    async def __call__(self) -> None:
        await generate()


@cappa.command(help='一An efficient fba command line interface', default_long=True)
@dataclass
class FbaCli:
    sql: Annotated[
        str,
        cappa.Arg(value_name='PATH', default='', show_default=False, help='Execute SQL scripts in transaction'),
    ]
    subcmd: cappa.Subcommands[Init | Run | Celery | Add | CodeGenerator | None] = None

    async def __call__(self) -> None:
        if self.sql:
            async with async_db_session.begin() as db:
                await execute_sql_scripts(db, self.sql)


def main() -> None:
    output = cappa.Output(error_format=f'{error_format}\n{output_help}')
    asyncio.run(cappa.invoke_async(FbaCli, version=__version__, output=output))
