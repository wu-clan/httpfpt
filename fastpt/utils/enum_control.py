#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum


def get_enum_values(enum_class):
    if issubclass(enum_class, Enum):
        return list(map(lambda ec: ec.value, enum_class))
    else:
        raise ValueError('获取枚举类所有属性值失败，传入了非枚举类参数')