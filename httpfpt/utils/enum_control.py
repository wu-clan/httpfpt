#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum


def get_enum_values(enum_class: type[Enum]) -> list:
    return list(map(lambda ec: ec.value, enum_class))
