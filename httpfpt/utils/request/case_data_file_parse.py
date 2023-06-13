#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import copy
from typing import List, Dict, Any

from httpfpt.schemas.case_data import CaseData


def get_request_data(*, file_data: dict, use_pydantic_verify: bool = False) -> List[Dict[str, Dict[str, Any]]]:
    """
    通过解析读取的测试用例文件数据, 获取用于数据驱动的请求数据

    :param file_data: 从测试用例数据文件读取的测试用例数据
    :param use_pydantic_verify: 是否将数据转换为 pydantic 模型
    :return:
    """
    try:
        config = file_data['config']
    except KeyError:
        raise ValueError('请求测试用力数据缺少 config 信息, 请检查测试用例文件内容')
    if config is None:
        raise ValueError('请求测试用力数据缺少 config 内容, 请检查测试用例文件内容')
    try:
        cases = file_data['test_steps']
    except KeyError:
        raise ValueError('请求测试用力数据缺少 test_steps 信息, 请检查测试用例文件内容')
    if cases is None:
        raise ValueError('请求测试用例数据缺少 test_steps 内容, 轻简查测试用例文件内容')
    if isinstance(cases, dict):
        if use_pydantic_verify:
            return [CaseData(**file_data).model_dump(by_alias=True)]
        else:
            return [file_data]
    elif isinstance(cases, list):
        case_list = []
        for case in cases:
            if isinstance(case, dict):
                test_steps = {'test_steps': case}
                data = copy.deepcopy(file_data)
                data.update(test_steps)
                if use_pydantic_verify:
                    case_list.append(CaseData(**data).model_dump(by_alias=True))
                else:
                    case_list.append(data)
            else:
                raise ValueError('请求测试用例数据 test_steps 格式错误, 请检查测试用例文件内容')
        return case_list
