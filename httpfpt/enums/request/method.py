#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import unique

from httpfpt.enums import StrEnum


@unique
class MethodType(StrEnum):
    get = 'GET'
    post = 'POST'
    put = 'PUT'
    delete = 'DELETE'
    patch = 'PATCH'
