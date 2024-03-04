#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os

from typing import Any

from httpfpt.common.log import log
from httpfpt.core.path_conf import httpfpt_path_config


def read_json_file(filepath: str | None = httpfpt_path_config.case_data_dir, *, filename: str, **kwargs) -> dict:
    """
    读取 json 文件

    :param filepath:
    :param filename:
    :param kwargs:
    :return:
    """
    if filepath is not None:
        filepath = os.path.join(filepath, filename)
    try:
        with open(filepath, encoding='utf-8') as f:  # type: ignore
            data = json.load(f, **kwargs)
    except Exception as e:
        log.error(f'文件 {filename} 读取错误: {e}')
        raise e
    if data is not None:
        return data
    else:
        log.warning(f'数据文件 {filename} 没有数据!')
        raise ValueError(f'数据文件 {filename} 没有数据! 请检查数据文件内容是否正确!')


def write_json_file(
    filepath: str | None = None, *, filename: str, data: Any = None, encoding: str = 'utf-8', mode: str = 'a', **kwargs
) -> None:
    """
    写入 json 文件

    :param filepath:
    :param filename:
    :param data:
    :param encoding:
    :param mode:
    :param kwargs:
    :return:
    """
    if filepath is not None:
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        _file = os.path.join(filepath, filename)
    else:
        _file = filename
    if not _file:
        log.warning('写入 json 文件失败，文件名为空')
        raise ValueError('写入 json 文件失败，文件名为空')
    try:
        with open(_file, encoding=encoding, mode=mode) as f:
            json.dump(data, f, ensure_ascii=False, **kwargs)
    except Exception as e:
        log.error(f'写入文件 "{filename}" 错误: {e}')
        raise e
    else:
        log.info(f'写入文件 {filename} 成功')
