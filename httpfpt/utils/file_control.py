#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glob
import os.path

from pathlib import Path
from typing import Optional, Tuple

from httpfpt.core.get_conf import PROJECT_NAME
from httpfpt.core.path_conf import TEST_CASE_PATH, YAML_DATA_PATH


def get_file_property(filepath: str) -> Tuple[str, str, str]:
    """
    获取文件属性

    :param filepath:
    :return:
    """
    file = Path(filepath)
    filename = file.name
    file_root_name = file.stem
    filetype = filename.split('.')[-1]
    return filename, file_root_name, filetype


def search_all_case_yaml_files(filepath: Optional[str] = None) -> list:
    """
    搜索指定项目目录下(包括子目录)所有测试用例数据文件

    :return:
    """
    yaml_filepath = os.path.join(YAML_DATA_PATH, f'{PROJECT_NAME}') if filepath is None else filepath
    files = glob.glob(os.path.join(yaml_filepath, '**', '*.yaml'), recursive=True) + glob.glob(
        os.path.join(yaml_filepath, '**', '*.yml'), recursive=True
    )
    return files


def search_all_testcase_files() -> list:
    """
    搜索指定项目目录下(包括子目录)所有测试用例文件

    :return:
    """
    files = glob.glob(os.path.join(TEST_CASE_PATH, f'{PROJECT_NAME}', '**', 'test_*.py'), recursive=True)
    return files
