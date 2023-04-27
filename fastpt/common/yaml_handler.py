#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Union, Optional, NoReturn

import yaml

from fastpt.common.log import log
from fastpt.core.path_conf import YAML_DATA_PATH, YAML_REPORT_PATH, TEST_DATA_PATH


def read_yaml(
    filepath: Optional[str] = YAML_DATA_PATH, *, filename: str
) -> Dict[str, Union[str, int, float, bool, List[Any], Dict[str, Any], None]]:
    """
    读取 yaml 文件

    :param filepath: 文件路径
    :param filename: 文件名
    :return:
    """
    if filepath is not None:
        _file = os.path.join(filepath, filename)
    else:
        _file = filename
    try:
        with open(_file, encoding='utf-8') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
    except Exception as e:
        log.error(f'文件 {filename} 读取错误: {e}')
        raise e
    if data is not None:
        return data
    else:
        log.warning(f'数据文件 {filename} 没有数据!')
        raise ValueError(f'数据文件 {filename} 没有数据! 请检查数据文件内容是否正确!')


def write_yaml(filepath: str, filename: str, data: Any = None, *, encoding: str = 'utf-8', mode: str = 'a') -> NoReturn:
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
        log.success(f'写入文件 {filename} 成功')
        return result


def write_yaml_report(
    filename: str = f'APITestResult_{datetime.now().strftime("%Y-%m-%d %H_%M_%S")}.yaml',
    *,
    data: Any,
    encoding: str = 'utf-8',
    mode: str = 'a',
    status: str,
) -> NoReturn:
    """
    写入 yaml 测试报告

    :param filename: 测试报告文件名
    :param data: 写入数据
    :param encoding: 文件编码格式
    :param mode: 文件写入模式
    :param status: 测试结果
    :return
    """
    status_upper = status.upper()
    if status_upper not in ('PASS', 'FAIL'):
        raise ValueError('yaml测试报告结果用力状态只允许"PASS","FAIL"')
    if not os.path.exists(YAML_REPORT_PATH):
        os.makedirs(YAML_REPORT_PATH)
    _file = os.path.join(YAML_REPORT_PATH, filename)
    try:
        with open(_file, encoding=encoding, mode=mode) as f:
            yaml.dump(data, f, allow_unicode=True)
    except Exception as e:
        log.error(f'写入 {filename} 测试报告失败: {e}')
        raise e
    else:
        log.success(f'写入 {filename} 测试报告成功')


def write_yaml_vars(data: dict) -> NoReturn:
    """
    写入 yaml 全部变量

    :param data:
    :return:
    """
    _file = os.path.join(TEST_DATA_PATH, 'global_vars.yaml')
    try:
        _vars = read_yaml(TEST_DATA_PATH, filename='global_vars.yaml')
        _vars.update(data)
        with open(_file, encoding='utf-8', mode='w') as f:
            yaml.dump(_vars, f, allow_unicode=True)
    except Exception as e:
        log.error(f'写入 global_vars.yaml 全局变量 {data} 错误: {e}')
    else:
        log.success(f'写入 global_vars.yaml 全局变量 {data} 成功')


def get_yaml_file(filepath: str = YAML_DATA_PATH, *, filename: str) -> str:
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
