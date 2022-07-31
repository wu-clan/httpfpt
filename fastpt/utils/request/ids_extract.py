#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def get_ids(request_data: list):
    """
    从请求数据获取数据驱动下的 ids 数据


    :param request_data: 请求数据
    :return:
    """
    ids = []
    for data in request_data:
        try:
            module = data['config']['module']
            name = data['test_steps']['name']
            case_id = data['test_steps']['case_id']
        except KeyError as e:
            raise ValueError('测试用例 ids 获取失败, 请检查测试用例数据是否符合规范: {}'.format(e))
        ids.append('module: {}, name: {}, case_id: {}'.format(module, name, case_id))
    return ids
