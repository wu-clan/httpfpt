#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import ast
from typing import Union

from jsonpath import findall

from httpfpt.common.errors import CorrelateTestCaseError, JsonPathFindError
from httpfpt.common.log import log
from httpfpt.common.variable_cache import variable_cache
from httpfpt.db.redis_db import redis_client
from httpfpt.utils.allure_control import allure_step
from httpfpt.utils.request.request_data_parse import RequestDataParse
from httpfpt.utils.request.vars_extractor import var_extractor


def exec_setup_testcase(parsed: RequestDataParse, setup_testcase: list) -> Union['RequestDataParse', None]:
    """
    执行前置关联测试用例

    :param parsed:
    :param setup_testcase:
    :return:
    """
    # 判断是否关联用例自身
    parsed_case_id = parsed.case_id
    for testcase in setup_testcase:
        error_text = '执行关联测试用例失败，禁止关联自身'
        if isinstance(testcase, dict):
            if testcase['case_id'] == parsed_case_id:
                raise CorrelateTestCaseError(error_text)
        elif isinstance(testcase, str):
            if testcase == parsed_case_id:
                raise CorrelateTestCaseError(error_text)

    # 判断关联测试用例是否存在
    all_case_id = ast.literal_eval(redis_client.get(f'{redis_client.prefix}::case_id::all'))
    for testcase in setup_testcase:
        error_text = '执行关联测试用例失败，未在测试用例中找到关联测试用例，请检查关联测试用例 case_id 是否存在'
        if isinstance(testcase, dict):
            if testcase['case_id'] not in all_case_id:
                raise CorrelateTestCaseError(error_text)
        elif isinstance(testcase, str):
            if testcase not in all_case_id:
                raise CorrelateTestCaseError(error_text)
        else:
            raise CorrelateTestCaseError('执行关联测试用例失败，关联测试用例参数类型错误')

    # 执行关联测试用例
    relate_count = 0
    for testcase in setup_testcase:
        # 用例中 testcase 参数为设置变量时
        if isinstance(testcase, dict):
            relate_count += 1
            relate_case_id = testcase['case_id']
            relate_case_filename = redis_client.get(f'{redis_client.prefix}::case_id_filename::{relate_case_id}')
            case_data = redis_client.get(f'{redis_client.prefix}::case_data::{relate_case_filename}')
            case_data = ast.literal_eval(case_data)
            case_data_test_steps = case_data['test_steps']
            if isinstance(case_data_test_steps, list):
                for case_test_steps in case_data_test_steps:
                    if relate_case_id == case_test_steps['case_id']:
                        relate_case_steps = case_test_steps
                        is_circular_relate(parsed_case_id, relate_case_steps)
                        # 重新组合测试用例
                        testcase_data = {
                            'test_steps': relate_case_steps,
                            'set_var_key': testcase['key'],
                            'set_var_jsonpath': testcase['jsonpath'],
                        }
                        case_data.update(testcase_data)
                        relate_testcase_set_var(case_data)
            else:
                relate_case_steps = case_data_test_steps
                is_circular_relate(parsed_case_id, relate_case_steps)
                testcase_data = {'set_var_key': testcase['key'], 'set_var_jsonpath': testcase['jsonpath']}
                case_data.update(testcase_data)
                relate_testcase_set_var(case_data)

        # 用例中 testcase 参数为直接关联测试用例时
        elif isinstance(testcase, str):
            relate_case_filename = redis_client.get(f'{redis_client.prefix}::case_id_filename::{testcase}')
            case_data = redis_client.get(f'{redis_client.prefix}::case_data::{relate_case_filename}')
            case_data = ast.literal_eval(case_data)
            case_data_test_steps = case_data['test_steps']
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
        # 应用关联测试用例变量到请求数据，使用模糊匹配，可能有优化效果
        request_data = parsed.request_data
        if '^' in str(request_data):
            parsed.request_data = var_extractor.relate_vars_replace(request_data)
            return parsed


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
                text = '关联测试用例执行失败，关联测试用例中存在引用当前测试用例为关联测试用例，导致循环引用'
                if isinstance(relate_testcase, dict):
                    if current_case_id == relate_testcase['case_id']:
                        raise CorrelateTestCaseError(text)
                else:
                    if current_case_id == relate_testcase:
                        raise CorrelateTestCaseError(text)


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
        variable_cache.set(testcase_data['set_var_key'], value[0])
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
