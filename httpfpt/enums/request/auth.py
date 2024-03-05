#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from httpfpt.enums import StrEnum


class AuthType(StrEnum):
    TOKEN = 'bearer_token'
    COOKIE = 'header_cookie'
