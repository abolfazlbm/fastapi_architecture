#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

from backend.core.path_conf import BASE_PATH

from .actions import *  # noqa: F403

# Import the project root directory
sys.path.append(str(BASE_PATH.parent))
