#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum, unique


@unique
class SqlType(str, Enum):
    select = 'SELECT'
    update = 'UPDATE'
    delete = 'DELETE'
