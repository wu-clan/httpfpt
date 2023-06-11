#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum, unique


@unique
class VarType(str, Enum):
    CACHE = 'cache'
    ENV = 'env'
    GLOBAL = 'global'
