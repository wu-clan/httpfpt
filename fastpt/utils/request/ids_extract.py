#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def get_values(request_data: list) -> list:
    """
    获取读取的 excel/yaml 数据,并取出数据中的 values 重新组合

    :param request_data: 读取的 excel 数据或者 yaml 数据
    :return: [(value1, value2, ...)] or [(value1, value2, ...), ..., (value1, value2, ...)]
    """

    new_data = []

    for _ in request_data:
        i = tuple(_.values())
        new_data.append(i)
    return new_data


def get_ids(request_data: list) -> list:
    """
    将请求数据中的 values 重新组合为 ids 格式

    :param request_data: 读取的 excel 数据或者 yaml 数据
    :return:
    """
    data = get_values(request_data)

    ids = []
    for d in data:
        ids.append(
            f'module: {d[0]}, case_id: {d[1]}, case_desc: {d[2]}, is_run: {d[3]}, method: {d[4]}, env: {d[5]}, '
            f'url: {d[6]}, params: {d[7]}, headers: {d[8]},data_type: {d[9]},data: {d[10]},files: {d[11]},'
            f'sql: {d[12]},assert: {d[13]},'
        )
    return ids
