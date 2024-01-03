#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy
import json
import sys

from typing import Any, Dict, List

from pydantic import ValidationError

from httpfpt.common.errors import RequestDataParseError
from httpfpt.common.log import log
from httpfpt.common.yaml_handler import read_yaml
from httpfpt.db.redis_db import redis_client
from httpfpt.schemas.case_data import CaseData
from httpfpt.utils.file_control import get_file_hash, get_file_property, search_all_case_yaml_files
from httpfpt.utils.pydantic_parser import parse_error


def clean_cache_data(clean_cache: bool) -> None:
    """
    清理 redis 缓存数据

    :param clean_cache:
    :return:
    """
    if clean_cache:
        redis_client.delete_prefix(redis_client.prefix, exclude=redis_client.token_prefix)


def case_data_init(pydantic_verify: bool) -> None:
    """
    初始化用例数据

    :param pydantic_verify:
    :return:
    """
    all_case_yaml_file = search_all_case_yaml_files()
    for case_yaml_file in all_case_yaml_file:
        case_data = read_yaml(None, filename=case_yaml_file)
        filename = get_file_property(case_yaml_file)[0]
        file_hash = get_file_hash(case_yaml_file)
        case_data.update({'filename': filename, 'file_hash': file_hash})
        redis_case_data = redis_client.get(f'{redis_client.case_data_prefix}:{filename}', logging=False)
        if redis_case_data is None:
            redis_client.set(f'{redis_client.case_data_prefix}:{filename}', json.dumps(case_data, ensure_ascii=False))
        else:
            redis_file_hash = json.loads(redis_case_data).get('file_hash')
            if file_hash != redis_file_hash:
                redis_client.rset(
                    f'{redis_client.case_data_prefix}:{filename}', json.dumps(case_data, ensure_ascii=False)
                )
    if pydantic_verify:
        case_data_list = redis_client.get_prefix(f'{redis_client.case_data_prefix}:')
        count: int = 0
        for case_data in case_data_list:
            try:
                CaseData.model_validate(json.loads(case_data))
            except ValidationError as e:
                count += parse_error(e)
        if count > 0:
            raise RequestDataParseError(f'测试用例数据校验失败，共有 {count} 处错误, 错误详情请查看日志')


def case_id_unique_verify() -> None:
    """
    获取所有用例 id

    :return:
    """
    all_case_id_dict: List[Dict[str, str | list]] = []
    all_case_id = []
    case_data_list = redis_client.get_prefix(f'{redis_client.case_data_prefix}:')
    redis_client.delete_prefix(f'{redis_client.case_id_file_prefix}:')
    for case_data in case_data_list:
        case_data = json.loads(case_data)
        filename = case_data['filename']
        try:
            steps = case_data['test_steps']
            if isinstance(steps, dict):
                case_id = steps['case_id']
                all_case_id.append(case_id)
                all_case_id_dict.append({f'{filename}': case_id})
                redis_client.set(f'{redis_client.case_id_file_prefix}:{case_id}', filename)
            if isinstance(steps, list):
                case_id_list = []
                for s in steps:
                    case_id = s['case_id']
                    case_id_list.append(case_id)
                    all_case_id.append(case_id)
                    redis_client.set(f'{redis_client.case_id_file_prefix}:{case_id}', filename)
                all_case_id_dict.append({f'{filename}': case_id_list})
        except KeyError:
            raise RequestDataParseError(f'测试用例数据文件 {filename} 结构错误，建议开启 pydantic 验证')
    # 检测用例 id 是否重复
    set_all_case_id = set(all_case_id)
    all_repeat_case_id = []
    if len(set_all_case_id) != len(all_case_id):
        for i in set_all_case_id:
            repeat_count = 0
            for j in all_case_id:
                if i == j:
                    repeat_count += 1
            # 输出重复用例 id 详情
            if repeat_count > 1:
                all_repeat_case_id_detail = []
                repeat_case_id_desc = {'case_id': i, 'count': repeat_count}
                for case_id_dict in all_case_id_dict:
                    for key in case_id_dict.keys():
                        file_case_id_list = case_id_dict[key]
                        repeat_index_list = []
                        if i in file_case_id_list:
                            if file_case_id_list.count(i) == 1:
                                repeat_index_list.append(file_case_id_list.index(i))
                            else:  # 无需判断多种条件，因为只有存在重复 id 才能执行至此，如果重复数量不为 1 则必定大于 1
                                for k in range(len(file_case_id_list)):
                                    if file_case_id_list.count(file_case_id_list[k]) > 1:
                                        repeat_index_list.append(k)
                            all_repeat_case_id_detail.append({'filename': f'{key}', 'index': repeat_index_list})
                repeat_case_id_desc.update({'detail': all_repeat_case_id_detail})
                all_repeat_case_id.append(repeat_case_id_desc)
    if len(all_repeat_case_id) > 0:
        redis_client.set(f'{redis_client.prefix}:case_id:repeated', 'true')
        log.error(f'运行失败, 检测到用例重复 case_id: {all_repeat_case_id[0]}')
        sys.exit(1)
    else:
        redis_client.delete(f'{redis_client.prefix}:case_id:repeated')
        redis_client.rset(f'{redis_client.prefix}:case_id_list', str(all_case_id))


def get_request_data(*, filename: str) -> List[Dict[str, Any]]:
    """
    获取用于测试用例数据驱动的请求数据

    :param filename: 测试用例数据文件名称
    :return:
    """
    case_data = json.loads(redis_client.get(f'{redis_client.case_data_prefix}:{filename}'))
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
