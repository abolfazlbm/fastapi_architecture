#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glob
import json
import os

from pathlib import Path
from typing import Any

import yaml

from backend.core.conf import settings
from backend.core.path_conf import LOCALE_DIR


class I18n:
    """International Manager"""

    def __init__(self):
        self.locales: dict[str, dict[str, Any]] = {}
        self.current_language: str = settings.I18N_DEFAULT_LANGUAGE

    def load_locales(self):
        """Loading language text"""
        patterns = [
            os.path.join(LOCALE_DIR, '*.json'),
            os.path.join(LOCALE_DIR, '*.yaml'),
            os.path.join(LOCALE_DIR, '*.yml'),
        ]

        lang_files = []

        for pattern in patterns:
            lang_files.extend(glob.glob(pattern))

        for lang_file in lang_files:
            with open(lang_file, 'r', encoding='utf-8') as f:
                lang = Path(lang_file).stem
                file_type = Path(lang_file).suffix[1:]
                match file_type:
                    case 'json':
                        self.locales[lang] = json.loads(f.read())
                    case 'yaml' | 'yml':
                        self.locales[lang] = yaml.full_load(f.read())

    def t(self, key: str, default: Any | None = None, **kwargs) -> str:
        """
        Translation functions

        :param key: Target text key, support dot separation, such as 'response.success'
        :param default: The default text when the target language text does not exist
        :param kwargs: variable parameters in target text
        :return:
        """
        keys = key.split('.')

        try:
            translation = self.locales[self.current_language]
        except KeyError:
            keys = 'error.language_not_found'
            translation = self.locales[settings.I18N_DEFAULT_LANGUAGE]

        for k in keys:
            if isinstance(translation, dict) and k in list(translation.keys()):
                translation = translation[k]
            else:
                # Pydantic Compatible
                if keys[0] == 'pydantic':
                    translation = None
                else:
                    translation = key

        if translation and kwargs:
            translation = translation.format(**kwargs)

        return translation or default


# Create i18n single case
i18n = I18n()

# Create a translation function instance
t = i18n.t
