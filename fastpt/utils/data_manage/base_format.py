#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def format_value(value_type: str):
    """
    根据数据类型格式化数据

    :param value_type:
    :return:
    """
    if value_type == 'string':
        v = ''
    elif value_type == 'integer':  # noqa: SIM114
        v = 0
    elif value_type == 'number':
        v = 0
    elif value_type == 'boolean':
        v = False
    elif value_type == 'object':
        v = {}
    elif value_type == 'array':
        v = [{}]
    elif value_type == 'arrayString':
        v = []
    else:
        raise Exception(f'存在不支持的类型：{value_type}')
    return v
