#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import json
import os
import shutil
import zipfile

from typing import Any

from fastapi import UploadFile

from backend.common.enums import PluginType, StatusType
from backend.common.exception import errors
from backend.core.conf import settings
from backend.core.path_conf import PLUGIN_DIR
from backend.database.redis import redis_client
from backend.plugin.tools import uninstall_requirements_async
from backend.utils.file_ops import install_git_plugin, install_zip_plugin
from backend.utils.timezone import timezone


class PluginService:
    """Plugin Service Class"""

    @staticmethod
    async def get_all() -> list[dict[str, Any]]:
        """Get all plugins"""
        keys = []
        result = []

        async for key in redis_client.scan_iter(f'{settings.PLUGIN_REDIS_PREFIX}:*'):
            keys.append(key)

        for info in await redis_client.mget(*keys):
            result.append(json.loads(info))

        return result

    @staticmethod
    async def changed() -> str | None:
        """Check whether the plug-in has changed"""
        return await redis_client.get(f'{settings.PLUGIN_REDIS_PREFIX}:changed')

    @staticmethod
    async def install(*, type: PluginType, file: UploadFile | None = None, repo_url: str | None = None) -> str:
        """
        Install plug-ins

        :param type: plugin type
        :param file: plugin zip compressed package
        :param repo_url: git repository address
        :return:
        """
        if type == PluginType.zip:
            if not file:
                raise errors.RequestError(msg='ZIP compressed package cannot be empty')
            return await install_zip_plugin(file)
        if not repo_url:
            raise errors.RequestError(msg='Git repository address cannot be empty')
        return await install_git_plugin(repo_url)

    @staticmethod
    async def uninstall(*, plugin: str):
        """
        Uninstall plug-in

        :param plugin: plugin name
        :return:
        """
        plugin_dir = os.path.join(PLUGIN_DIR, plugin)
        if not os.path.exists(plugin_dir):
            raise errors.NotFoundError(msg='plugin does not exist')
        await uninstall_requirements_async(plugin)
        bacup_dir = os.path.join(PLUGIN_DIR, f'{plugin}.{timezone.now().strftime("%Y%m%d%H%M%S")}.backup')
        shutil.move(plugin_dir, bacup_dir)
        await redis_client.delete(f'{settings.PLUGIN_REDIS_PREFIX}:{plugin}')
        await redis_client.set(f'{settings.PLUGIN_REDIS_PREFIX}:changed', 'ture')

    @staticmethod
    async def update_status(*, plugin: str):
        """
        Update plugin status

        :param plugin: plugin name
        :return:
        """
        plugin_info = await redis_client.get(f'{settings.PLUGIN_REDIS_PREFIX}:{plugin}')
        if not plugin_info:
            raise errors.NotFoundError(msg='plugin does not exist')
        plugin_info = json.loads(plugin_info)

        # Update persistent cache status
        new_status = (
            str(StatusType.enable.value)
            if plugin_info['plugin']['enable'] == str(StatusType.disable.value)
            else str(StatusType.disable.value)
        )
        plugin_info['plugin']['enable'] = new_status
        await redis_client.set(f'{settings.PLUGIN_REDIS_PREFIX}:{plugin}', json.dumps(plugin_info, ensure_ascii=False))

    @staticmethod
    async def build(*, plugin: str) -> io.BytesIO:
        """
        Package plug-in as zip compressed package

        :param plugin: plugin name
        :return:
        """
        plugin_dir = os.path.join(PLUGIN_DIR, plugin)
        if not os.path.exists(plugin_dir):
            raise errors.NotFoundError(msg='plugin does not exist')

        bio = io.BytesIO()
        with zipfile.ZipFile(bio, 'w') as zf:
            for root, dirs, files in os.walk(plugin_dir):
                dirs[:] = [d for d in dirs if d != '__pycache__']
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=plugin_dir)
                    zf.write(file_path, os.path.join(plugin, arcname))

        bio.seek(0)
        return bio


plugin_service: PluginService = PluginService()
