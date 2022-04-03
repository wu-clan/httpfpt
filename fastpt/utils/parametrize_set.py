#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastpt.common.excel_operate import read_excel
from fastpt.common.yaml_operate import read_yaml

# Ps: 严格遵循 APITestCaseTEMPLATE 用例文件中的请求参数, 主要包括参数名,参数位置...
# 如果你使用此工具,请务必确保你在使用数据驱动时的用例文件格式与模板用例文件中的格式(参数名和顺序)完全一致

__args = ['model', 'ID', 'UseCase', 'method', 'url', 'params', 'headers', 'body', 'body_type', 'status_code', 'msg',
          'result', 'tester']


def req_values(filename: str, sheet='Sheet1') -> list:
    """
    获取请求数据,并取出数据中的values重新组合

    :param filename: 文件名
    :param sheet: excel工作表,只有数据文件为excel时生效
    :return: [(value1, value2, ...)] or [(value1, value2, ...), ..., (value1, value2, ...)]
    """
    file_type = str(filename.split('.')[-1])
    if file_type not in ('xlsx', 'yaml'):
        raise ValueError('请求数据文件只允许"xlsx"或"yaml"格式文件')

    new_data = []

    if file_type == 'xlsx':
        excel_data = read_excel(filename=filename, sheet=sheet)
        for _ in excel_data:
            _ = tuple(_.values())
            new_data.append(_)
        return new_data

    if file_type == 'yaml':
        excel_data = read_yaml(filename=filename)
        for _ in excel_data:
            _ = tuple(_.values())
            new_data.append(_)
        return new_data


def req_args() -> list:
    """
    请求参数集

    :return:
    """
    args = __args
    return args


def param_ids(req_data: list) -> list:
    """
    parametrize ids set

    :param req_data: 请求数据
    :return:
    """
    ids = [
        'model: {}, ID: {}, UseCase: {}, method: {}, url: {}, params: {}, headers: {}, body: {}, body_type: {}, status_code: {}, msg: {}, result: {}, tester: {}'.format(
            model, ID, UseCase, method, url, params, headers, body, body_type, status_code, msg, result, tester) for
        model, ID, UseCase, method, url, params, headers, body, body_type, status_code, msg, result, tester in req_data]
    return ids


def serialize_req_args(model, ID, UseCase, method, url, params, headers, body, body_type, status_code, msg, result,
                       tester) -> dict:
    """
    序列化请求参数

    :param model: 测试模块
    :param ID: 用例ID
    :param UseCase: 测试用例名
    :param method: 请求方式
    :param url: 请求连接
    :param params: 请求参数
    :param headers: 请求头
    :param body: 请求体
    :param body_type: 请求体类型
    :param status_code: 预期状态码
    :param msg: 与其返回内容
    :param result: 测试结果
    :param tester: 测试人员
    :return:
    """
    # data = {'model': model, 'ID': ID, 'UseCase': UseCase, 'method': method, 'url': url, 'params': params,
    #         'headers': headers, 'body': body, 'type': type, 'msg': msg, 'status_code': status_code, 'result': result,
    #         'tester': tester}
    data = dict(
        zip(__args,
            [model, ID, UseCase, method, url, params, headers, body, body_type, status_code, msg, result, tester]))
    return data
