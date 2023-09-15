#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import ast
import copy
import sys
from typing import List, Dict, Any, Union

from pydantic import ValidationError

from httpfpt.common.errors import RequestDataParseError
from httpfpt.common.log import log
from httpfpt.common.yaml_handler import read_yaml
from httpfpt.db.redis_db import redis_client
from httpfpt.schemas.case_data import CaseData
from httpfpt.utils.file_control import search_all_case_yaml_files, get_file_property
from httpfpt.utils.pydantic_parser import parse_error


def case_data_init(pydantic_verify: bool = False) -> None:
    """
    初始化用例数据

    :param pydantic_verify:
    :return:
    """
    all_case_yaml_file = search_all_case_yaml_files()
    for case_yaml_file in all_case_yaml_file:
        case_data = read_yaml(None, filename=case_yaml_file)
        filename = get_file_property(case_yaml_file)[0]
        case_data.update({'filename': filename})
        redis_client.rset(f'{redis_client.prefix}::case_data::{filename}', str(case_data))
    if pydantic_verify:
        case_data_list = redis_client.get_prefix(f'{redis_client.prefix}::case_data::')
        count: int = 0
        for case_data in case_data_list:
            try:
                CaseData.model_validate(ast.literal_eval(case_data))
            except ValidationError as e:
                count += parse_error(e)
        if count > 0:
            raise RequestDataParseError(f'测试用例数据校验失败，共有 {count} 处错误, 错误详情请查看日志')


def case_id_unique_verify(case_id_verify: bool) -> None:
    """
    获取所有用例 id

    :param case_id_verify:
    :return:
    """
    if case_id_verify:
        all_case_id_dict: List[Dict[str, Union[str, list]]] = []
        case_data_list = redis_client.get_prefix(f'{redis_client.prefix}::case_data::')
        for case_data in case_data_list:
            case_data = ast.literal_eval(case_data)
            filename = case_data['filename']
            try:
                steps = case_data['test_steps']
                if isinstance(steps, dict):
                    all_case_id_dict.append({f'{filename}': steps['case_id']})
                if isinstance(steps, list):
                    case_id_list = []
                    for s in steps:
                        case_id_list.append(s['case_id'])
                    all_case_id_dict.append({f'{filename}': case_id_list})
            except KeyError:
                raise RequestDataParseError(f'测试用例数据文件 {filename} 结构错误，建议开启 pydantic 验证')
        all_case_id = []
        for case_id_dict in all_case_id_dict:
            for case_id_values in case_id_dict.values():
                if isinstance(case_id_values, str):
                    all_case_id.append(case_id_values)
                else:
                    for case_id in case_id_values:
                        all_case_id.append(case_id)
        set_all_case_id = set(all_case_id)
        all_repeat_case_id_desc = []
        if len(set_all_case_id) != len(all_case_id):
            all_repeat_case_id_detail = []
            for i in set_all_case_id:
                repeat_count = 0
                for j in all_case_id:
                    if i == j:
                        repeat_count += 1
                if repeat_count > 1:
                    repeat_case_id_desc = {'case_id': i, 'count': repeat_count}
                    for case_id_dict in all_case_id_dict:
                        for key in case_id_dict.keys():
                            if i == case_id_dict[key] or i in case_id_dict[key]:
                                all_repeat_case_id_detail.append(
                                    {'filename': f'{key}', 'case_index': case_id_dict[key].index(i)}
                                )
                                print(i)
                    repeat_case_id_desc.update({'detail': all_repeat_case_id_detail})
                    all_repeat_case_id_desc.append(repeat_case_id_desc)
        if len(all_repeat_case_id_desc) > 0:
            redis_client.set(f'{redis_client.prefix}::case_id::repeated', 'true')
            log.error(f'运行失败, 检测到用例重复 case_id: {all_repeat_case_id_desc}')
            sys.exit(1)
        else:
            redis_client.delete(f'{redis_client.prefix}::case_id::repeated')
            redis_client.rset(f'{redis_client.prefix}::case_id::all', str(all_case_id))


def get_request_data(*, filename: str) -> List[Dict[str, Any]]:
    """
    获取用于测试用例数据驱动的请求数据

    :param filename: 测试用例数据文件名称
    :return:
    """
    case_data = ast.literal_eval(redis_client.get(f'{redis_client.prefix}::case_data::{filename}'))
    config_error = f'请求测试用例数据文件 {filename} 缺少 config 信息, 请检查测试用例文件内容'
    test_steps_error = f'请求测试用例数据文件 {filename} 缺少 test_steps 信息, 请检查测试用例文件内容'
    try:
        config = case_data['config']
    except KeyError:
        raise RequestDataParseError(config_error)
    if config is None:
        raise RequestDataParseError(config_error)

    try:
        cases = case_data['test_steps']
    except KeyError:
        raise RequestDataParseError(test_steps_error)
    if cases is None:
        raise RequestDataParseError(test_steps_error)

    if isinstance(cases, dict):
        return [case_data]
    elif isinstance(cases, list):
        case_list = []
        for case in cases:
            if isinstance(case, dict):
                test_steps = {'test_steps': case}
                data = copy.deepcopy(case_data)
                data.update(test_steps)
                case_list.append(data)
            else:
                raise RequestDataParseError(test_steps_error)
        return case_list
    else:
        raise RequestDataParseError(f'请求测试用例数据文件 {filename} 格式错误, 请检查用例数据文件内容')