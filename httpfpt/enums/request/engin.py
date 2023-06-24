#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from httpfpt.enums import StrEnum


class EnginType(StrEnum):
    requests = 'requests'
    httpx = 'httpx'
