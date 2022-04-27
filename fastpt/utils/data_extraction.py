#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Ps: 严格遵循 APITestCaseTEMPLATE 用例文件中的请求参数, 主要包括参数名,参数位置...
# 如果你使用此工具,请务必确保你在使用数据驱动时的用例文件格式与模板用例文件中的格式(参数名和顺序)完全一致


def get_values(request_data: list) -> list:
    """
    获取请求数据,并取出数据中的values重新组合

    :param request_data: 读取的excel数据或者yaml数据
    :return: [(value1, value2, ...)] or [(value1, value2, ...), ..., (value1, value2, ...)]
    """

    new_data = []

    for _ in request_data:
        i = tuple(_.values())
        new_data.append(i)
    return new_data


def get_ids(request_data: list) -> list:
    """
    将请求数据中的values重新组合为ids格式

    :param request_data: 读取的excel数据或者yaml数据
    :return:
    """
    data = get_values(request_data)

    ids = [
        'model: {}, ID: {}, UseCase: {}, method: {}, url: {}, params: {}, headers: {}, body: {}, body_type: {}, status_code: {}, msg: {}, result: {}, tester: {}'.format(
            model, ID, UseCase, method, url, params, headers, body, body_type, status_code, msg, result, tester) for
        model, ID, UseCase, method, url, params, headers, body, body_type, status_code, msg, result, tester in data
    ]
    return ids
