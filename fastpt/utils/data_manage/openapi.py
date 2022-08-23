#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastpt.common.json_handler import read_json_file


def import_swagger3_json(file: str):
    """
    导入 swagger3 测试用例

    :return:
    """
    data = read_json_file(None, filename=file)
    # 校验 openapi 版本
    if data['openapi'].split('.')[0] != 3:
        raise ValueError('导入失败, openapi 版本不符合要求, 请使用 openapi3 版本')
    # todo


