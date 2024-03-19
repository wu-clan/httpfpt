#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from httpfpt.common.errors import RequestDataParseError


def get_ids(request_data: list) -> list:
    """
    从请求数据获取数据驱动下的 ids 数据

    :param request_data: 请求数据
    :return:
    """
    ids = []
    for data in request_data:
        try:
            module = data['config']['module']
            case_id = data['test_steps']['case_id']
        except KeyError as e:
            raise RequestDataParseError('测试用例 ids 获取失败, 请检查测试用例数据是否符合规范: {}'.format(e))
        ids.append('module: {}, case_id: {}'.format(module, case_id))
    return ids
