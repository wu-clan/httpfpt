#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum


class SeverityType(str, Enum):
    Blocker = 'blocker'
    Critical = 'critical'
    Normal = 'normal'
    Minor = 'minor'
    Trivial = 'trivial'
