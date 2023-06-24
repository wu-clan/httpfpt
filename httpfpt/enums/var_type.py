#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import unique

from httpfpt.enums import StrEnum


@unique
class VarType(StrEnum):
    CACHE = 'cache'
    ENV = 'env'
    GLOBAL = 'global'
