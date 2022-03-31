#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

import toml

from fastpt.common.log import log


def read_toml(filepath: str, filename: str) -> dict:
    """
    读取 toml 文件
    :param filepath: 文件路径
    :param filename: 文件名
    :return:
    """
    _filename = os.path.join(filepath, filename)
    try:
        data = toml.load(_filename)
    except TypeError as e:
        log.error(f'文件 {_filename} 内存在格式错误 \n {e}')
        raise e
    except toml.TomlDecodeError as e:
        log.critical('toml文件解析错误')
        raise e
    else:
        return data


def write_toml(filepath: str, filename: str, data: dict, encoding: str = 'utf-8', mode: str = 'a', encoder=None) -> str:
    """
    将字典写入包含 TOML 格式数据的文件
    :param filepath: 文件路径
    :param filename: 文件名称
    :param data: 写入内容
    :param encoding: 文件内容编码格式
    :param mode: 文件写入模式
    :param encoder: TOML 编码器
    :return:
    """
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    _file = os.path.join(filepath, filename)
    try:
        with open(_file, encoding=encoding, mode=mode) as f:
            result = toml.dump(data, f, encoder=encoder)
    except TypeError as e:
        log.error(f'写入文件 "{_file}" 错误 \n {e}')
        raise e
    else:
        log.success(f'写入文件 {_file} 成功')
        return result
