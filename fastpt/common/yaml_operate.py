#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
from datetime import datetime

import yaml

from fastpt.common.log import log
from fastpt.core.path_conf import YAML_DATA_PATH, YAML_REPORT_PATH

curr_time = time.strftime('%Y-%m-%d %H_%M_%S')


def read_yaml(filepath: str = YAML_DATA_PATH, *, filename: str) -> dict:
    """
    读取 yaml 文件
    :param filepath: 文件路径
    :param filename: 文件名
    :return:
    """
    _filename = os.path.join(filepath, filename)
    try:
        with open(_filename, encoding='utf-8') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
    except Exception as e:
        log.error(f'文件 {_filename} 不存在 \n {e}')
        raise e
    else:
        return data


def write_yaml(filepath: str, filename: str, data=None, encoding: str = 'utf-8', mode: str = 'a'):
    """
    将数据写入包含 yaml 格式数据的文件
    :param filepath: 文件路径
    :param filename: 文件名
    :param data: 数据
    :param encoding: 文件内容编码格式
    :param mode: 文件写入模式
    :return:
    """
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    _file = os.path.join(filepath, filename)
    try:
        with open(_file, encoding=encoding, mode=mode) as f:
            result = yaml.dump(data, f, allow_unicode=True)
    except Exception as e:
        log.error(f'写入文件 "{_file}" 错误 \n {e}')
        raise e
    else:
        log.success(f'写入文件 {_file} 成功')
        return result


def write_yaml_report(filename: str = f'APITestResult_{datetime.now()}.yaml', *, data=None, encoding: str = 'utf-8',
                      mode: str = 'a'):
    """
    写入yaml测试报告
    :param filename: 测试报告文件名
    :param data: 写入数据
    :param encoding: 文件编码格式
    :param mode: 文件写入模式
    :return
    """
    if not os.path.exists(YAML_REPORT_PATH):
        os.makedirs(YAML_REPORT_PATH)
    _file = os.path.join(YAML_REPORT_PATH, filename)
    try:
        with open(_file, encoding=encoding, mode=mode) as f:
            result = yaml.dump(data, f, allow_unicode=True)
    except Exception as e:
        log.error(f'写入yaml测试报告失败 \n {e}')
        raise e
    else:
        log.success('写入yaml测试报告成功')
        return result


def get_yaml(filepath: str = YAML_DATA_PATH, *, filename: str) -> str:
    """
    获取 yaml 文件
    :param filepath: 文件路径
    :param filename: 文件名
    :return:
    """
    _file = os.path.join(filepath, filename)
    if not os.path.exists(_file):
        raise FileNotFoundError(f'测试数据文件 {filename} 不存在')
    return _file
