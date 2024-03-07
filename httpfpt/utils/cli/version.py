#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

from importlib.resources import read_text

import cappa

from httpfpt.utils.rich_console import console


def get_version() -> None:
    """获取版本号"""
    ver = read_text('httpfpt', '__init__.py')
    mob = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", ver, re.MULTILINE)
    if mob:
        console.print('\n🔥 HttpFpt', mob.group(1))
    else:
        raise cappa.Exit('未查询到版本号', code=1)
