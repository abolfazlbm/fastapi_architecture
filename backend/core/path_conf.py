#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path

# Project root directory
BASE_PATH = Path(__file__).resolve().parent.parent

# alembic migration file storage path
ALEMBIC_VERSION_DIR = BASE_PATH / 'alembic' / 'versions'

# Log file path
LOG_DIR = BASE_PATH / 'log'

# Static resource directory
STATIC_DIR = BASE_PATH / 'static'

# Upload file directory
UPLOAD_DIR = STATIC_DIR / 'upload'

# Offline IP database path
IP2REGION_XDB = STATIC_DIR / 'ip2region.xdb'

# Plugin Directory
PLUGIN_DIR = BASE_PATH / 'plugin'

# International File Directory
LOCALE_DIR = BASE_PATH / 'locale'
