#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

import uvicorn

if __name__ == '__main__':
    # Why standalone this startup file: https://stackoverflow.com/questions/64003384

    # DEBUG:
    # If you like to DEBUG in the IDE, you can directly right-click to launch this file in the IDE
    # If you like to debug through print, it is recommended to start the service using fba cli

    # Warning:
    # If you are starting this file through the python command, please follow the following:
    # 1. Install dependencies through uv according to the official documentation
    # 2. The command line space is located in the backend directory
    try:
        uvicorn.run(
            app='backend.main:app',
            host='127.0.0.1',
            port=8000,
            reload=True,
            reload_excludes=[os.path.abspath('../.venv')],
        )
    except Exception as e:
        raise e
