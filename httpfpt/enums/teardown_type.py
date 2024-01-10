#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from httpfpt.enums import StrEnum


class TeardownType(StrEnum):
    SQL = 'sql'
    HOOK = 'hook'
    EXTRACT = 'extract'
    ASSERT = 'assert'
    WAIT_TIME = 'wait_time'
