#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum, unique


@unique
class AuthType(str, Enum):
    bearer_token = 'bearer_token'
