#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glob
import os.path
import re
from typing import Tuple

from fastpt.core.get_conf import PROJECT_NAME
from fastpt.core.path_conf import YAML_DATA_PATH, TEST_CASE_PATH


def get_file_property(filepath: str) -> Tuple[str, str, str]:
    """
    获取文件属性

    :param filepath:
    :return:
    """
    filename = re.split(r'/|\'|\\|\\\\', filepath)[-1]
    file_real_name = '.'.join(filename.split('.')[:-1])
    filetype = filename.split('.')[-1]
    return filename, file_real_name, filetype


def search_all_case_yaml_files() -> list:
    """
    搜索指定项目目录下(包括子目录)所有测试用例数据文件

    :return:
    """
    files = glob.glob(os.path.join(YAML_DATA_PATH, f'{PROJECT_NAME}', '**\\', '*.yaml'), recursive=True) + glob.glob(
        os.path.join(YAML_DATA_PATH, f'{PROJECT_NAME}', '**\\', '*.yml'), recursive=True)
    return files


def search_all_test_case_files() -> list:
    """
    搜索指定项目目录下(包括子目录)所有测试用例文件

    :return:
    """
    files = glob.glob(os.path.join(TEST_CASE_PATH, f'{PROJECT_NAME}', '**\\', 'test_*.py'), recursive=True)
    return files
