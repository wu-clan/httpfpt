#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import os

from pathlib import Path
from typing import Any

import yaml

from httpfpt.common.log import log
from httpfpt.core.path_conf import httpfpt_path
from httpfpt.utils.time_control import get_current_time


def read_yaml(filepath: str, filename: str | None = None) -> dict[str, Any]:
    """
    读取 yaml 文件

    :param filepath: 文件路径
    :param filename: 文件名
    :return:
    """
    if filename:
        filepath = os.path.join(filepath, filename)
    try:
        with open(filepath, encoding='utf-8') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
    except Exception as e:
        log.error(f'文件 {filename} 读取错误: {e}')
        raise e
    if data is not None:
        return data
    else:
        log.warning(f'数据文件 {filename} 没有数据!')
        raise ValueError(f'数据文件 {filename} 没有数据! 请检查数据文件内容是否正确!')


def write_yaml(filepath: str, filename: str, data: Any = None, *, encoding: str = 'utf-8', mode: str = 'a') -> None:
    """
    将数据写入包含 yaml 格式数据的文件

    :param filepath: 文件路径
    :param filename: 文件名
    :param data: 数据
    :param encoding: 文件内容编码格式
    :param mode: 文件写入模式
    :return:
    """
    _file = os.path.join(filepath, filename)
    if not Path(_file).parent.exists():
        Path(_file).parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(_file, encoding=encoding, mode=mode) as f:
            result = yaml.dump(data, f, allow_unicode=True)
    except Exception as e:
        log.error(f'写入文件 "{filename}" 错误: {e}')
        raise e
    else:
        log.info(f'写入文件成功: {filename} ')
        return result


def write_yaml_report(
    filename: str = f'APITestResult_{get_current_time("%Y-%m-%d %H_%M_%S")}.yaml',
    *,
    data: Any,
    encoding: str = 'utf-8',
    mode: str = 'a',
) -> None:
    """
    写入 yaml 测试报告

    :param filename: 测试报告文件名
    :param data: 写入数据
    :param encoding: 文件编码格式
    :param mode: 文件写入模式
    :return
    """
    _yaml_report_path = httpfpt_path.yaml_report_dir
    if not os.path.exists(_yaml_report_path):
        os.makedirs(_yaml_report_path)
    _file = os.path.join(_yaml_report_path, filename)
    try:
        with open(_file, encoding=encoding, mode=mode) as f:
            yaml.dump(data, f, allow_unicode=True)
    except Exception as e:
        log.error(f'写入 {filename} 测试报告失败: {e}')
        raise e
    else:
        log.info(f'写入测试报告成功: {filename}')


def write_yaml_vars(data: dict) -> None:
    """
    写入 yaml 全部变量

    :param data:
    :return:
    """
    _file = os.path.join(httpfpt_path.data_path, 'global_vars.yaml')
    try:
        _vars = read_yaml(httpfpt_path.data_path, filename='global_vars.yaml')
        _vars.update(data)
        with open(_file, encoding='utf-8', mode='w') as f:
            yaml.dump(_vars, f, allow_unicode=True)
    except Exception as e:
        log.error(f'写入 global_vars.yaml 全局变量 {data} 错误: {e}')
    else:
        log.info(f'写入全局变量成功: global_vars.yaml -> {data}')


def get_yaml_file(filepath: str = httpfpt_path.case_data_dir, *, filename: str) -> str:
    """
    获取 yaml 测试数据文件

    :param filepath: 文件路径
    :param filename: 文件名
    :return:
    """
    _file = os.path.join(filepath, filename)
    if not os.path.exists(_file):
        raise FileNotFoundError(f'测试数据文件 {filename} 不存在')
    return _file
