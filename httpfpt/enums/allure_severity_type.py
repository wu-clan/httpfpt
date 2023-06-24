#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from httpfpt.enums import StrEnum


class SeverityType(StrEnum):
    blocker = 'blocker'
    critical = 'critical'
    normal = 'normal'
    minor = 'minor'
    trivial = 'trivial'
