#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os.path

import dotenv

from fastpt.common.log import log
from fastpt.core.path_conf import RUN_ENV_PATH


def get_env_dict(filepath: str) -> dict:
    """
    获取 env 字典信息

    :param filepath:
    :return:
    """
    dotenv.find_dotenv(filepath, raise_error_if_not_found=True)
    env_dict = dict(dotenv.dotenv_values(filepath))
    return env_dict


def write_env(filepath: str, filename: str, key: str, value: str):
    """
    写入 env 字典信息

    :param filepath:
    :param filename:
    :param key:
    :param value:
    :return:
    """
    _file = os.path.join(filepath, filename)
    try:
        dotenv.set_key(_file, key, value)
    except Exception as e:
        log.error(f'写入 {filename} 环境变量错误: {e}')
        raise e
    else:
        log.success(f'写入 {filename} 环境变量成功')