#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum, unique


@unique
class MethodType(str, Enum):
    get = 'GET'
    post = 'POST'
    put = 'PUT'
    delete = 'DELETE'
    patch = 'PATCH'
