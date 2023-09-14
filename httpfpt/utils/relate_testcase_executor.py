#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from typing import List, Dict, Union

from jsonpath import findall
from pydantic import ValidationError

from httpfpt.common.errors import CorrelateTestCaseError, JsonPathFindError
from httpfpt.common.log import log
from httpfpt.common.variable_cache import VariableCache
from httpfpt.common.yaml_handler import read_yaml
from httpfpt.db.redis_db import redis_client
from httpfpt.schemas.case_data import CaseData
from httpfpt.utils.allure_control import allure_step
from httpfpt.utils.file_control import search_all_case_yaml_files, get_file_property
from httpfpt.utils.pydantic_parser import parse_error
from httpfpt.utils.request.request_data_parse import RequestDataParse
from httpfpt.utils.request.vars_extractor import VarsExtractor


def get_all_testcase_id(case_data_list: list) -> list:
    """
    获取所有测试用例 id

    :param case_data_list:
    :return:
    """
    all_case_id_dict: List[Dict[str, Union[str, list]]] = []
    for case_data in case_data_list:
        steps = case_data['test_steps']
        if isinstance(steps, dict):
            all_case_id_dict.append({f'{case_data["filename"]}': steps['case_id']})
        if isinstance(steps, list):
            cl = []
            for i in steps:
                cl.append(i['case_id'])
            all_case_id_dict.append({f'{case_data["filename"]}': cl})
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
        for i in set_all_case_id:
            re_count = 0
            for j in all_case_id:
                if i == j:
                    re_count += 1
            if re_count > 1:
                re_case_id_desc = {'case_id': i, 'count': re_count}
                all_re_case_id_detail = []
                for case_id_dict in all_case_id_dict:
                    for key in case_id_dict.keys():
                        if i in case_id_dict[key]:
                            all_re_case_id_detail.append({'file': f'{key}', 'index': case_id_dict[key].index(i)})
                re_case_id_desc.update(
                    {
                        'detail': all_re_case_id_detail if len(all_re_case_id_detail) > 1 else all_re_case_id_detail[0],
                    }
                )
                all_repeat_case_id_desc.append(re_case_id_desc)
    if len(all_repeat_case_id_desc) > 0:
        redis_client.set(f'{redis_client.prefix}:is_repeat_case_id', 'true')
        log.error(f'运行失败, 检测到用例数据重复 case_id: {all_repeat_case_id_desc}')
        sys.exit(1)
    else:
        redis_client.delete(f'{redis_client.prefix}:is_repeat_case_id')
        redis_client.rset(f'{redis_client.prefix}:all_case_id', str(all_case_id))
    return all_case_id


def get_all_testcase_data(pydantic_verify: bool = False) -> list:
    """
    获取所有测试用例数据

    :param pydantic_verify:
    :return:
    """
    all_yaml_file = search_all_case_yaml_files()
    all_case_data = []
    if not redis_client.redis.get(f'{redis_client.prefix}:is_repeat_case_id'):
        redis_all_case_data = redis_client.get(f'{redis_client.prefix}:all_case_data')
        if redis_all_case_data:
            redis_all_case_data_len = redis_client.get(f'{redis_client.prefix}:all_case_data_len')
            if redis_all_case_data_len is not None:
                if int(redis_all_case_data_len) == len(all_yaml_file):
                    all_case_data = eval(redis_all_case_data)
            else:
                redis_client.set(f'{redis_client.prefix}:all_case_data_len', len(all_yaml_file))
    if len(all_case_data) == 0:
        for file in all_yaml_file:
            read_data = read_yaml(None, filename=file)
            read_data.update({'filename': get_file_property(file)[0]})
            all_case_data.append(read_data)
        redis_client.rset(f'{redis_client.prefix}:all_case_data', str(all_case_data))
    if pydantic_verify:
        for case_data in all_case_data:
            try:
                count: int = 0
                CaseData.model_validate(case_data)
            except ValidationError as e:
                count = parse_error(e)
            if count > 0:
                raise CorrelateTestCaseError(f'测试用例数据校验失败，共有 {count} 处错误, 错误详情请查看日志')
    return all_case_data


def exec_setup_testcase(parsed: RequestDataParse, setup_testcase: list) -> Union['RequestDataParse', None]:
    """
    执行前置关联测试用例

    :param parsed:
    :param setup_testcase:
    :return:
    """
    parsed_case_id = parsed.case_id
    # 判断是否关联用例自身
    for testcase in setup_testcase:
        if isinstance(testcase, dict):
            if testcase['case_id'] == parsed_case_id:
                raise CorrelateTestCaseError('执行关联测试用例失败，禁止关联自身')
        elif isinstance(testcase, str):
            if testcase == parsed_case_id:
                raise CorrelateTestCaseError('执行关联测试用例失败，禁止关联自身')

    all_case_data = get_all_testcase_data()
    all_case_id = redis_client.get(f'{redis_client.prefix}:all_case_id') or get_all_testcase_id(all_case_data)
    relate_count = 0

    # 判断关联测试用例是否存在
    for testcase in setup_testcase:
        if isinstance(testcase, dict):
            relate_case_id = testcase['case_id']
            if relate_case_id not in str(all_case_id):
                raise CorrelateTestCaseError('未在测试用例中找到关联测试用例，请检查关联测试用例 case_id 是否存在')
        elif isinstance(testcase, str):
            if testcase not in str(all_case_id):
                raise CorrelateTestCaseError('未在测试用例中找到关联测试用例，请检查关联测试用例 case_id 是否存在')

    # 获取关联测试用例数据
    for case_data in all_case_data:
        # 单个测试用例步骤
        case_data_test_steps = case_data['test_steps']
        # 单个测试用例步骤下的所有 case 的 case_id
        case_id_list = []
        if isinstance(case_data_test_steps, list):
            for i in case_data_test_steps:
                case_id_list.append(i['case_id'])
        else:
            case_id_list.append(case_data_test_steps['case_id'])
        # 判断关联用例
        for testcase in setup_testcase:
            # 用例中 testcase 参数为设置变量时
            if isinstance(testcase, dict):
                relate_case_id = testcase['case_id']
                if relate_case_id in str(case_id_list):
                    relate_count += 1
                    if isinstance(case_data_test_steps, list):
                        for case_test_steps in case_data_test_steps:
                            if relate_case_id == case_test_steps['case_id']:
                                # 使命名更清晰
                                relate_case_steps = case_test_steps
                                # 避免循环关联
                                is_circular_relate(parsed_case_id, relate_case_steps)
                                # 重新组合测试用例
                                new_data = {
                                    'test_steps': relate_case_steps,
                                    'set_var_key': testcase['key'],
                                    'set_var_jsonpath': testcase['jsonpath'],
                                }
                                case_data.update(new_data)
                                relate_testcase_set_var(case_data)
                    else:
                        relate_case_steps = case_data_test_steps
                        is_circular_relate(parsed_case_id, relate_case_steps)
                        new_data = {'set_var_key': testcase['key'], 'set_var_jsonpath': testcase['jsonpath']}
                        case_data.update(new_data)
                        relate_testcase_set_var(case_data)

            # 用例中 testcase 参数为直接关联测试用例时
            elif isinstance(testcase, str):
                if testcase in str(case_id_list):
                    if isinstance(case_data_test_steps, list):
                        for case_test_steps in case_data_test_steps:
                            if testcase == case_test_steps['case_id']:
                                relate_case_steps = case_test_steps
                                is_circular_relate(parsed_case_id, relate_case_steps)
                                new_data = {'test_steps': relate_case_steps}
                                case_data.update(new_data)
                                relate_testcase_exec(case_data)
                    else:
                        relate_case_steps = case_data_test_steps
                        is_circular_relate(parsed_case_id, relate_case_steps)
                        relate_testcase_exec(case_data)

    if relate_count > 0:
        # 再次解析请求数据，应用关联测试用例设置的变量到请求数据
        parsed.request_data = VarsExtractor().relate_vars_replace(parsed.request_data)
        return parsed
    else:
        return None


def is_circular_relate(current_case_id: str, relate_case_steps: dict) -> None:
    """
    判断是否循环关联

    :param current_case_id:
    :param relate_case_steps:
    :return:
    """
    try:
        relate_case_setup_testcase = relate_case_steps['setup']['testcase']
    except KeyError:
        pass
    else:
        if relate_case_setup_testcase is not None:
            for relate_testcase in relate_case_setup_testcase:
                if isinstance(relate_testcase, dict):
                    if current_case_id == relate_testcase['case_id']:
                        raise CorrelateTestCaseError('关联测试用例执行失败，在关联测试用例中，存在引用当前测试用例为关联测试用例，导致循环引用')  # noqa: E501
                else:
                    if current_case_id == relate_testcase:
                        raise CorrelateTestCaseError('关联测试用例执行失败，在关联测试用例中，存在引用当前测试用例为关联测试用例，导致循环引用')  # noqa: E501


def relate_testcase_set_var(testcase_data: dict) -> None:
    """
    关联测试用例设置变量

    :param testcase_data:
    :return:
    """
    from httpfpt.common.send_request import send_request

    msg = '🔗 执行关联测试用例变量提取：{}'.format(testcase_data['test_steps']['case_id'])
    log.debug(msg)
    allure_step(msg, '此文件为空')
    response = send_request.send_request(testcase_data, log_data=False, relate_testcase=True)
    value = findall(testcase_data['set_var_jsonpath'], response)
    if value:
        VariableCache().set(testcase_data['set_var_key'], value[0])
    else:
        raise JsonPathFindError('jsonpath 取值失败，表达式: {}'.format(testcase_data['set_var_jsonpath']))


def relate_testcase_exec(testcase_data: dict) -> None:
    """
    关联测试用例执行

    :param testcase_data:
    :return:
    """
    from httpfpt.common.send_request import send_request

    msg = '🔗 执行关联测试用例：{}'.format(testcase_data['test_steps']['case_id'])
    log.debug(msg)
    allure_step(msg, '此文件为空')
    send_request.send_request(testcase_data, log_data=False, relate_testcase=True)
