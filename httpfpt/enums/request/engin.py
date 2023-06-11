#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum


class EnginType(str, Enum):
    requests = 'requests'
    httpx = 'httpx'
