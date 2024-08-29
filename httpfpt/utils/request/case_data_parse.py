#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import sys

from collections import defaultdict

import pytest

from pydantic import ValidationError

from httpfpt.common.errors import RequestDataParseError
from httpfpt.common.log import log
from httpfpt.common.yaml_handler import read_yaml
from httpfpt.db.redis import redis_client
from httpfpt.schemas.case_data import CaseCacheData
from httpfpt.utils.file_control import get_file_hash, get_file_property, search_all_case_data_files
from httpfpt.utils.pydantic_parser import parse_error
from httpfpt.utils.request.ids_extract import get_ids


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
    all_case_data_files = search_all_case_data_files()
    for case_data_file in all_case_data_files:
        case_data = read_yaml(case_data_file)
        filename = get_file_property(case_data_file)[0]
        file_hash = get_file_hash(case_data_file)
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
                CaseCacheData.model_validate(json.loads(case_data))
            except ValidationError as e:
                count += parse_error(e)
        if count > 0:
            raise RequestDataParseError(f'测试用例数据校验失败，共有 {count} 处错误, 错误详情请查看日志')


def case_id_unique_verify() -> None:
    """
    获取所有用例 id

    :return:
    """
    all_case_id_dict: list[dict[str, str | list[str]]] = []
    all_case_id = []
    case_id_count = defaultdict(int)
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
                all_case_id_dict.append({filename: [case_id]})
                case_id_count[case_id] += 1
                redis_client.set(f'{redis_client.case_id_file_prefix}:{case_id}', filename)
            if isinstance(steps, list):
                case_id_list = [s['case_id'] for s in steps]
                all_case_id.extend(case_id_list)
                all_case_id_dict.append({filename: case_id_list})
                for case_id in case_id_list:
                    case_id_count[case_id] += 1
                    redis_client.set(f'{redis_client.case_id_file_prefix}:{case_id}', filename)
        except KeyError:
            raise RequestDataParseError(f'测试用例数据文件 {filename} 结构错误，建议开启 pydantic 验证')

    all_repeat_case_id = [
        {'case_id': case_id, 'count': count, 'detail': []} for case_id, count in case_id_count.items() if count > 1
    ]

    for repeat_case in all_repeat_case_id:
        for case_data_dict in all_case_id_dict:
            for key, case_id_list in case_data_dict.items():
                repeat_index_list = [i for i, cid in enumerate(case_id_list) if cid == repeat_case['case_id']]
                if repeat_index_list:
                    repeat_case['detail'].append({'filename': key, 'index': repeat_index_list})

    if all_repeat_case_id:
        redis_client.set(f'{redis_client.prefix}:case_id:repeated', 'true')
        log.error(f'运行失败, 检测到用例重复 case_id: {all_repeat_case_id[0]}')
        sys.exit(1)
    else:
        redis_client.delete(f'{redis_client.prefix}:case_id:repeated')
        redis_client.rset(f'{redis_client.prefix}:case_id_list', str(all_case_id))


def get_testcase_data(*, filename: str) -> tuple[list, list]:
    """
    获取测试用例数据

    :param filename: 测试用例数据文件名称
    :return:
    """
    case_data = json.loads(redis_client.get(f'{redis_client.case_data_prefix}:{filename}'))
    config_error = f'请求测试用例数据文件 {filename} 缺少 config 信息, 请检查测试用例文件内容'
    test_steps_error = f'请求测试用例数据文件 {filename} 缺少 test_steps 信息, 请检查测试用例文件内容'

    config = case_data.get('config')
    if config is None:
        raise RequestDataParseError(config_error)

    steps = case_data.get('test_steps')
    if steps is None:
        raise RequestDataParseError(test_steps_error)

    if isinstance(steps, dict):
        ids = get_ids(case_data)
        mark = get_testcase_mark(case_data)
        if mark is not None:
            ddt_data = pytest.param(case_data, marks=[getattr(pytest.mark, m) for m in mark])
        else:
            ddt_data = case_data
        return [ddt_data], ids
    elif isinstance(steps, list):
        _ddt_data_list = []
        marked_ddt_data_list = []
        for case in steps:
            if isinstance(case, dict):
                _case_data = {'config': config, 'test_steps': case}
                _ddt_data_list.append(_case_data)
                mark = get_testcase_mark(_case_data)
                if mark is not None:
                    marked_ddt_data_list.append(pytest.param(_case_data, marks=[getattr(pytest.mark, m) for m in mark]))
                else:
                    marked_ddt_data_list.append(_case_data)
            else:
                raise RequestDataParseError(test_steps_error)
        ids = get_ids(_ddt_data_list)
        return marked_ddt_data_list, ids
    else:
        raise RequestDataParseError(f'请求测试用例数据文件 {filename} 格式错误, 请检查用例数据文件内容')


def get_testcase_mark(case_data: dict) -> list[str] | None:
    try:
        mark = case_data['test_steps']['mark']
    except (KeyError, TypeError):
        try:
            mark = case_data['config']['mark']
        except (KeyError, TypeError):
            mark = None
    if mark is not None:
        if not isinstance(mark, list):
            raise RequestDataParseError(
                '测试用例数据解析失败, 参数 test_steps:mark 或 config:mark 不是有效的 list 类型'
            )
        else:
            for m in mark:
                if not isinstance(m, str):
                    raise RequestDataParseError(
                        '测试用例数据解析失败, 参数 test_steps:mark 或 config:mark 不是有效的 list[str] 类型'
                    )
    return mark
