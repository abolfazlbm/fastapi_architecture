#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pydantic import Field

from backend.common.schema import SchemaBase


class GetCaptchaDetail(SchemaBase):
    """Verification code details"""

    image_type: str = Field(description='image type')
    image: str = Field(description='image content')
