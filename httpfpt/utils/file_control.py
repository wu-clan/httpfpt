#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import glob
import os.path

from pathlib import Path

from httpfpt.core.get_conf import httpfpt_config
from httpfpt.core.path_conf import httpfpt_path


def get_file_property(filepath: str) -> tuple[str, str, str]:
    """
    获取文件属性

    :param filepath:
    :return:
    """
    file = Path(filepath)
    filename = file.name
    file_root_name = file.stem
    filetype = file.suffix[1:]
    return filename, file_root_name, filetype


def search_all_case_data_files(filepath: str | None = None) -> list:
    """
    搜索指定项目目录下(包括子目录)所有测试用例数据文件

    :return:
    """
    case_data_filepath = (
        os.path.join(httpfpt_path.case_data_dir, f'{httpfpt_config.PROJECT_NAME}') if filepath is None else filepath
    )
    files = (
        glob.glob(os.path.join(case_data_filepath, '**', '*.yaml'), recursive=True)
        + glob.glob(os.path.join(case_data_filepath, '**', '*.yml'), recursive=True)
        + glob.glob(os.path.join(case_data_filepath, '**', '*.json'), recursive=True)
    )
    return files


def search_all_testcase_files() -> list:
    """
    搜索指定项目目录下(包括子目录)所有测试用例文件

    :return:
    """
    files = glob.glob(
        os.path.join(httpfpt_path.testcase_dir, f'{httpfpt_config.PROJECT_NAME}', '**', 'test_*.py'), recursive=True
    )
    return files


def get_file_hash(filepath: str) -> str:
    """
    获取文件 hash (hash256) 值

    :param filepath:
    :return:
    """
    import hashlib

    with open(filepath, 'rb') as f:
        contents = f.read()
        file_hash = hashlib.sha256(contents).hexdigest()
    return file_hash
