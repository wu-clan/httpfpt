#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from httpfpt.enums import StrEnum


class CaseDataType(StrEnum):
    JSON = 'json'
    YAML = 'yaml'
    YML = 'yml'
