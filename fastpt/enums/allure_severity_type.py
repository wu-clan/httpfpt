#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum


class SeverityType(str, Enum):
    blocker = 'blocker'
    critical = 'critical'
    normal = 'normal'
    minor = 'minor'
    trivial = 'trivial'
