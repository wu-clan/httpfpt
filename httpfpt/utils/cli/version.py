#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import re

from importlib.resources import read_text

import cappa

from httpfpt.utils.rich_console import console


def get_version(cli: bool = True) -> str | None:
    """获取版本号"""
    ver = read_text('httpfpt', '__init__.py')
    mob = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", ver, re.MULTILINE)
    if mob:
        version = mob.group(1)
        if cli:
            console.print('')
            console.print(f'HTTPFPT: [cyan]{version}[/]')
        return version
    else:
        raise cappa.Exit('\n❌ 未查询到版本号', code=1)
