#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import os
import re
import zipfile

import aiofiles

from dulwich import porcelain
from fastapi import UploadFile
from sqlparse import split

from backend.common.enums import FileType
from backend.common.exception import errors
from backend.common.log import log
from backend.core.conf import settings
from backend.core.path_conf import PLUGIN_DIR, UPLOAD_DIR
from backend.database.redis import redis_client
from backend.plugin.tools import install_requirements_async
from backend.utils.re_verify import is_git_url
from backend.utils.timezone import timezone


def build_filename(file: UploadFile) -> str:
    """
    Build file name

    :param file: FastAPI Upload file object
    :return:
    """
    timestamp = int(timezone.now().timestamp())
    filename = file.filename
    file_ext = filename.split('.')[-1].lower()
    new_filename = f'{filename.replace(f".{file_ext}", f"_{timestamp}")}.{file_ext}'
    return new_filename


def upload_file_verify(file: UploadFile) -> None:
    """
    File verification

    :param file: FastAPI Upload file object
    :return:
    """
    filename = file.filename
    file_ext = filename.split('.')[-1].lower()
    if not file_ext:
        raise errors.RequestError(msg='Unknown file type')

    if file_ext == FileType.image:
        if file_ext not in settings.UPLOAD_IMAGE_EXT_INCLUDE:
            raise errors.RequestError(msg='This image format is not supported for the time being')
        if file.size > settings.UPLOAD_IMAGE_SIZE_MAX:
            raise errors.RequestError(msg='The picture exceeds the maximum limit, please reselect')
    elif file_ext == FileType.video:
        if file_ext not in settings.UPLOAD_VIDEO_EXT_INCLUDE:
            raise errors.RequestError(msg='This video format is not supported for the time being')
        if file.size > settings.UPLOAD_VIDEO_SIZE_MAX:
            raise errors.RequestError(msg='Video exceeds the maximum limit, please reselect')


async def upload_file(file: UploadFile) -> str:
    """
    Upload file

    :param file: FastAPI Upload file object
    :return:
    """
    filename = build_filename(file)
    try:
        async with aiofiles.open(os.path.join(UPLOAD_DIR, filename), mode='wb') as fb:
            while True:
                content = await file.read(settings.UPLOAD_READ_SIZE)
                if not content:
                    break
                await fb.write(content)
    except Exception as e:
        log.error(f'Upload file {filename} failed: {str(e)}')
        raise errors.RequestError(msg='Upload file failed')
    await file.close()
    return filename


async def install_zip_plugin(file: UploadFile | str) -> str:
    """
    Install the ZIP plug-in

    :param file: FastAPI Upload file object or file full path
    :return:
    """
    if isinstance(file, str):
        async with aiofiles.open(file, mode='rb') as fb:
            contents = await fb.read()
    else:
        contents = await file.read()
    file_bytes = io.BytesIO(contents)
    if not zipfile.is_zipfile(file_bytes):
        raise errors.RequestError(msg='Plugin compression package format is illegal')
    with zipfile.ZipFile(file_bytes) as zf:
        # Verify the compressed package
        plugin_namelist = zf.namelist()
        plugin_dir_name = plugin_namelist[0].split('/')[0]
        if not plugin_namelist:
            raise errors.RequestError(msg='Plugin compression package content is illegal')
        if (
            len(plugin_namelist) <= 3
            or f'{plugin_dir_name}/plugin.toml' not in plugin_namelist
            or f'{plugin_dir_name}/README.md' not in plugin_namelist
        ):
            raise errors.RequestError(msg='Required files are missing in the plug-in compression package')

        # Is the plug-in available for installation
        plugin_name = re.match(
            r'^([a-zA-Z0-9_]+)',
            file.split(os.sep)[-1].split('.')[0].strip()
            if isinstance(file, str)
            else file.filename.split('.')[0].strip(),
        ).group()
        full_plugin_path = os.path.join(PLUGIN_DIR, plugin_name)
        if os.path.exists(full_plugin_path):
            raise errors.ConflictError(msg='This plugin is installed')
        else:
            os.makedirs(full_plugin_path, exist_ok=True)

        # Unzip (install)
        members = []
        for member in zf.infolist():
            if member.filename.startswith(plugin_dir_name):
                new_filename = member.filename.replace(plugin_dir_name, '')
                if new_filename:
                    member.filename = new_filename
                    members.append(member)
        zf.extractall(full_plugin_path, members)

    await install_requirements_async(plugin_dir_name)
    await redis_client.set(f'{settings.PLUGIN_REDIS_PREFIX}:changed', 'ture')

    return plugin_name


async def install_git_plugin(repo_url: str) -> str:
    """
    Install the Git plugin

    :param repo_url:
    :return:
    """
    match = is_git_url(repo_url)
    if not match:
        raise errors.RequestError(msg='Git repository address format is illegal')
    repo_name = match.group('repo')
    if os.path.exists(os.path.join(PLUGIN_DIR, repo_name)):
        raise errors.ConflictError(msg=f'{repo_name} plugin installed')
    try:
        porcelain.clone(repo_url, os.path.join(PLUGIN_DIR, repo_name), checkout=True)
    except Exception as e:
        log.error(f' plugin installation failed: {e}')
        raise errors.ServerError(msg='Plugin installation failed, please try again later') from e

    await install_requirements_async(repo_name)
    await redis_client.set(f'{settings.PLUGIN_REDIS_PREFIX}:changed', 'ture')

    return repo_name


async def parse_sql_script(filepath: str) -> list[str]:
    """
    Parsing SQL scripts

    :param filepath: script file path
    :return:
    """
    if not os.path.exists(filepath):
        raise errors.NotFoundError(msg='SQL script file does not exist')

    async with aiofiles.open(filepath, mode='r', encoding='utf-8') as f:
        contents = await f.read(1024)
        while additional_contents := await f.read(1024):
            contents += additional_contents

    statements = split(contents)
    for statement in statements:
        if not any(statement.lower().startswith(_) for _ in ['select', 'insert']):
            raise errors.RequestError(msg='Illegal operations exist in the SQL script file, only SELECT and INSERT')

    return statements
