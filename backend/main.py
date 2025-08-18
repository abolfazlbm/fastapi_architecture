#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.text import Text

from backend import console
from backend.core.registrar import register_app
from backend.plugin.tools import get_plugins, install_requirements
from backend.utils.timezone import timezone

_log_prefix = f'{timezone.to_str(timezone.now(), "%Y-%m-%d %H:%M:%S.%M0")} | {"INFO": <8} | - | '
console.print(Text(f'{_log_prefix} detects plugin dependency...', style='bold cyan'))

_plugins = get_plugins()

with Progress(
    SpinnerColumn(finished_text=f'[bold green]{_log_prefix} plugin ready[/]'),
    TextColumn('{task.completed}/{task.total}', style='bold green'),
    TimeElapsedColumn(),
    console=console,
) as progress:
    task = progress.add_task('Installation plugin dependencies...', total=len(_plugins))
    for plugin in _plugins:
        install_requirements(plugin)
        progress.advance(task)

console.print(Text(f'{_log_prefix} starts the service...', style='bold magenta'))

app = register_app()
