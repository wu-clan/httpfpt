#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from httpfpt.enums import StrEnum


class SetupType(StrEnum):
    TESTCASE = 'testcase'
    SQL = 'sql'
    HOOK = 'hook'
    WAIT_TIME = 'wait_time'
