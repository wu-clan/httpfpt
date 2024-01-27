#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

import dotenv

from httpfpt.common.log import log


def get_env_dict(filepath: str) -> dict:
    """
    获取 env 字典信息

    :param filepath:
    :return:
    """
    dotenv.find_dotenv(filepath, raise_error_if_not_found=True)
    env_dict = dict(dotenv.dotenv_values(filepath))
    return env_dict


def write_env_vars(filepath: str, filename: str, key: str, value: str) -> None:
    """
    写入 env 信息

    :param filepath:
    :param filename:
    :param key:
    :param value:
    :return:
    """
    _file = os.path.join(filepath, filename)
    key_upper = key.upper()
    try:
        dotenv.set_key(_file, key_upper, value)
    except Exception as e:
        log.error(f'写入 {filename} 环境变量 {key_upper}={value} 错误: {e}')
        raise e
    else:
        log.info(f'写入环境变量成功: {filename} -> {key_upper}={value}')
