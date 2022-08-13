#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import copy
from typing import Union, List


def get_request_data(file_data: Union[dict, list]) -> List[dict]:
    """
    通过解析读取的测试用例文件数据, 获取用于数据驱动的请求数据

    :param file_data: 从测试用例文件读取的测试用例数据
    :return:
    """
    # yaml
    if isinstance(file_data, dict):
        try:
            cases = file_data['test_steps']
        except KeyError:
            raise ValueError('请求测试用力数据缺少 test_steps 信息, 请检查测试用例文件内容')
        if cases is None:
            raise ValueError('请求测试用例数据缺少 test_steps 内容, 轻简查测试用例文件内容')
        elif isinstance(cases, dict):
            return [file_data]
        elif isinstance(cases, list):
            case_list = []
            for case in cases:
                if isinstance(case, dict):
                    test_steps = {'test_steps': case}
                    data = copy.deepcopy(file_data)
                    data.update(test_steps)
                    case_list.append(data)
                else:
                    raise ValueError('请求测试用例数据 test_steps 格式错误, 请检查测试用例文件内容')
            return case_list
    # excel
    # 方案设计:
    # 1. 简化形式, 将测试用例数据作为 json 格式写入 config 和 test_steps 两列, 非常好实现, 但会导致用例太难维护, 体验极差.
    # 2. 常规模式, 列设定请求数据对应 config 和 test_steps 下的一级参数, 然后将测试用例数据作为参数要求格式写入多列, 对体验
    # 会有很大提升, 但仍没有 yaml 使用简便.
    # excel 支持只是时间问题, 欢迎 PR 方案2, 方案1默认拒绝
    elif isinstance(file_data, list):
        raise ValueError('新版本以暂停对 excel 数据文件的支持')
    else:
        raise ValueError('获取请求数据失败, 传入了非法格式的测试用例数据, 请使用从测试用例文件读取的测试用例数据')
