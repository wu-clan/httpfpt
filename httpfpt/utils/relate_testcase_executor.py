#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import ast
import json

from jsonpath import findall

from httpfpt.common.errors import CorrelateTestCaseError, JsonPathFindError
from httpfpt.common.log import log
from httpfpt.common.variable_cache import variable_cache
from httpfpt.db.redis import redis_client
from httpfpt.enums.setup_type import SetupType
from httpfpt.utils.allure_control import allure_step
from httpfpt.utils.request.vars_extractor import var_extractor


def exec_setup_testcase(parsed_data: dict, setup_testcase: str | dict) -> dict | None:
    """
    执行前置关联测试用例

    :param parsed_data:
    :param setup_testcase:
    :return:
    """
    # 判断是否关联用例自身
    parsed_case_id = parsed_data['case_id']
    error_text = '执行关联测试用例失败，禁止关联自身'
    if isinstance(setup_testcase, dict):
        if setup_testcase['case_id'] == parsed_case_id:
            raise CorrelateTestCaseError(error_text)
    elif isinstance(setup_testcase, str):
        if setup_testcase == parsed_case_id:
            raise CorrelateTestCaseError(error_text)

    # 判断关联测试用例是否存在
    all_case_id = ast.literal_eval(redis_client.get(f'{redis_client.prefix}:case_id_list'))
    error_text = '执行关联测试用例失败，未在测试用例中找到关联测试用例，请检查关联测试用例 case_id 是否存在'
    if isinstance(setup_testcase, dict):
        if setup_testcase['case_id'] not in all_case_id:
            raise CorrelateTestCaseError(error_text)
    elif isinstance(setup_testcase, str):
        if setup_testcase not in all_case_id:
            raise CorrelateTestCaseError(error_text)

    # 执行关联测试用例
    relate_count = 0
    # 用例中 testcase 参数为更新请求数据或提取变量时
    if isinstance(setup_testcase, dict):
        relate_count += 1
        relate_case_id = setup_testcase['case_id']
        relate_case_filename = redis_client.get(f'{redis_client.case_id_file_prefix}:{relate_case_id}')
        case_data = redis_client.get(f'{redis_client.case_data_prefix}:{relate_case_filename}')
        case_data = json.loads(case_data)
        case_data_test_steps = case_data['test_steps']
        if isinstance(case_data_test_steps, list):
            for case_test_steps in case_data_test_steps:
                if relate_case_id == case_test_steps['case_id']:
                    relate_case_steps = case_test_steps
                    is_circular_relate(parsed_case_id, relate_case_steps)
                    if setup_testcase.get('request') is not None:
                        testcase_data = {
                            'test_steps': relate_case_steps,
                            'update_request_data': setup_testcase['request'],
                        }
                        case_data.update(testcase_data)
                        response = relate_testcase_exec_with_new_request_data(case_data)
                        # 使用更新请求数据后的请求响应提取变量
                        if setup_testcase.get('response') is not None:
                            testcase_data = {
                                'set_var_response': setup_testcase['response'],
                            }
                            relate_testcase_extract_with_response(testcase_data, response)
                    else:
                        if setup_testcase.get('response') is not None:
                            testcase_data = {
                                'test_steps': relate_case_steps,
                                'set_var_response': setup_testcase['response'],
                            }
                            case_data.update(testcase_data)
                            relate_testcase_extract(case_data)
        else:
            relate_case_steps = case_data_test_steps
            is_circular_relate(parsed_case_id, relate_case_steps)
            if setup_testcase.get('request') is not None:
                testcase_data = {'update_request_data': setup_testcase['request']}
                case_data.update(testcase_data)
                response = relate_testcase_exec_with_new_request_data(case_data)
                if setup_testcase.get('response') is not None:
                    testcase_data = {'set_var_response': setup_testcase['response']}
                    relate_testcase_extract_with_response(testcase_data, response)
            else:
                if setup_testcase.get('response') is not None:
                    testcase_data = {'set_var_response': setup_testcase['response']}
                    case_data.update(testcase_data)
                    relate_testcase_extract(case_data)

    # 用例中 testcase 参数为直接关联测试用例时
    elif isinstance(setup_testcase, str):
        relate_case_filename = redis_client.get(f'{redis_client.case_id_file_prefix}:{setup_testcase}')
        case_data = redis_client.get(f'{redis_client.case_data_prefix}:{relate_case_filename}')
        case_data = json.loads(case_data)
        case_data_test_steps = case_data['test_steps']
        if isinstance(case_data_test_steps, list):
            for case_test_steps in case_data_test_steps:
                if setup_testcase == case_test_steps['case_id']:
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
        # 应用关联测试用例变量到请求数据，使用模糊匹配，可能有解析速度优化效果
        if '^' in str(parsed_data):
            relate_parsed_data = var_extractor.relate_vars_replace(parsed_data)
            return relate_parsed_data


def is_circular_relate(current_case_id: str, relate_case_steps: dict) -> None:
    """
    判断是否循环关联

    :param current_case_id:
    :param relate_case_steps:
    :return:
    """
    relate_case_setup_testcases = []
    try:
        relate_case_setup = relate_case_steps['setup']
        if relate_case_setup:
            for setup in relate_case_setup:
                for key, value in setup.items():
                    if key == SetupType.TESTCASE:
                        if isinstance(value, str):
                            relate_case_setup_testcases.append(value)
                        if isinstance(value, dict):
                            relate_case_setup_testcases.append(value['case_id'])
    except KeyError:
        pass
    else:
        if relate_case_setup_testcases:
            for relate_testcase in relate_case_setup_testcases:
                text = '关联测试用例执行失败，关联测试用例中的前置关联测试用例包含当前测试用例，导致循环引用'
                if current_case_id == relate_testcase:
                    raise CorrelateTestCaseError(text)


def relate_testcase_extract(testcase_data: dict) -> None:
    """
    关联测试用例提取变量

    :param testcase_data:
    :return:
    """
    from httpfpt.common.send_request import send_request

    msg = f'>>> 执行关联测试用例变量提取：{testcase_data["test_steps"]["case_id"]}'
    log.info(msg)
    allure_step(msg, '此文件为空')
    response = send_request.send_request(testcase_data, log_data=False, relate_log=True)
    relate_testcase_extract_with_response(testcase_data, response)
    log.info('<<< 关联测试用例变量提取执行完成')


def relate_testcase_extract_with_response(testcase_data: dict, response: dict) -> None:
    """
    关联测试用例提取变量（基于请求响应）

    :param testcase_data:
    :param response:
    :return:
    """
    for s in testcase_data['set_var_response']:
        value = findall(s['jsonpath'], response)
        if value:
            variable_cache.set(s['key'], value[0], tag='relate_testcase')
        else:
            raise JsonPathFindError('jsonpath 取值失败，表达式: {}'.format(s['jsonpath']))


def relate_testcase_exec_with_new_request_data(testcase_data: dict) -> dict:
    """
    关联测试用例（使用新请求数据）执行

    :param testcase_data:
    :return:
    """
    from httpfpt.common.send_request import send_request

    msg = f'>>> 执行关联测试用例（使用新请求数据）：{testcase_data["test_steps"]["case_id"]}'
    log.info(msg)
    allure_step(msg, '此文件为空')
    for u in testcase_data['update_request_data']:
        keys = u['jsonpath'].split('.')[1:]
        new_request_data = {}
        current_level = new_request_data
        for key in keys[:-1]:
            current_level[key] = {}
            current_level = current_level[key]
        current_level[keys[-1]] = u['value']
        testcase_data['test_steps']['request'].update(new_request_data)
        log.info(f'更新关联测试用例请求数据：{new_request_data}')
    response = send_request.send_request(testcase_data, log_data=False, relate_log=True)
    log.info('<<< 关联测试用例（使用新请求数据）执行完成')
    return response


def relate_testcase_exec(testcase_data: dict) -> None:
    """
    关联测试用例执行

    :param testcase_data:
    :return:
    """
    from httpfpt.common.send_request import send_request

    msg = f'>>> 执行关联测试用例：{testcase_data["test_steps"]["case_id"]}'
    log.info(msg)
    allure_step(msg, '此文件为空')
    send_request.send_request(testcase_data, log_data=False, relate_log=True)
    log.info('<<< 关联测试用例执行完成')
