#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum


class IntEnum(int, Enum):
    """整型枚举"""

    pass


class StrEnum(str, Enum):
    """字符串枚举"""

    pass
