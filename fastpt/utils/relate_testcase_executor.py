#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import NoReturn

from jsonpath import jsonpath

from fastpt.common.log import log
from fastpt.common.variable_cache import VariableCache
from fastpt.common.yaml_handler import read_yaml
from fastpt.db.redis_db import RedisDB
from fastpt.utils.allure_control import allure_step
from fastpt.utils.file_control import search_all_case_yaml_files
from fastpt.utils.request.request_data_parse import RequestDataParse
from fastpt.utils.request.vars_extractor import VarsExtractor


def __old_get_all_testcase_data() -> list:
    """
    获取所有测试用例数据

    :return:
    """
    all_yaml_file = search_all_case_yaml_files()
    all_case_data = []
    for file in all_yaml_file:
        read_data = read_yaml(None, filename=file)
        all_case_data.append(read_data)
    return all_case_data


def __old_get_all_testcase_id(case_data_list: list) -> list:
    """
    获取所有测试用例 id

    :param case_data_list:
    :return:
    """
    all_case_id = []
    for case_data in case_data_list:
        steps = case_data['test_steps']
        if isinstance(steps, dict):
            all_case_id.append(steps['case_id'])
        if isinstance(steps, list):
            for i in steps:
                all_case_id.append(i['case_id'])
    return all_case_id


def get_all_testcase_data() -> list:
    """
    获取所有测试用例数据

    :return:
    """
    all_yaml_file = search_all_case_yaml_files()
    redis_all_case_data = RedisDB().get('aap_all_case_data')
    if redis_all_case_data:
        redis_all_case_data_len = RedisDB().get('aap_all_case_data_len')
        if redis_all_case_data_len is not None:
            if int(redis_all_case_data_len) == len(all_yaml_file):
                return eval(redis_all_case_data)
        else:
            RedisDB().set('aap_all_case_data_len', len(all_yaml_file))
    all_case_data = []
    for file in all_yaml_file:
        read_data = read_yaml(None, filename=file)
        all_case_data.append(read_data)
    RedisDB().rset('aap_all_case_data', str(all_case_data))
    return all_case_data


def get_all_testcase_id(case_data_list: list) -> list:
    """
    获取所有测试用例 id

    :param case_data_list:
    :return:
    """
    all_case_id = []
    case_id_len = 0
    for case_data in case_data_list:
        steps = case_data['test_steps']
        if isinstance(steps, dict):
            case_id_len += 1
        if isinstance(steps, list):
            for _ in steps:
                case_id_len += 1
    redis_case_id_len = RedisDB().get('aap_all_case_id_len')
    if redis_case_id_len is not None:
        if int(redis_case_id_len) == case_id_len:
            redis_case_id = RedisDB().get('aap_all_case_id')
            return eval(redis_case_id)
    else:
        RedisDB().set('aap_all_case_id_len', case_id_len)
    for case_data in case_data_list:
        steps = case_data['test_steps']
        if isinstance(steps, dict):
            all_case_id.append(steps['case_id'])
        if isinstance(steps, list):
            for i in steps:
                all_case_id.append(i['case_id'])
    RedisDB().rset('aap_all_case_id', str(all_case_id))
    return all_case_id


def exec_setup_testcase(parsed: RequestDataParse, setup_testcase: list) -> NoReturn:
    """
    执行前置关联测试用例

    :param parsed:
    :param setup_testcase:
    :return:
    """
    # 判断是否关联用例自身
    for testcase in setup_testcase:
        if isinstance(testcase, dict):
            if testcase['case_id'] == parsed.case_id:
                raise ValueError('执行关联测试用例失败，不能关联自身')
        elif isinstance(testcase, str):
            if testcase == parsed.case_id:
                raise ValueError('执行关联测试用例失败，不能关联自身')

    # all_case_data = __old_get_all_testcase_data()
    # all_case_id = __old_get_all_testcase_id(all_case_data)
    all_case_data = get_all_testcase_data()
    all_case_id = get_all_testcase_id(all_case_data)

    # 判断关联测试用例是否存在
    for testcase in setup_testcase:
        if isinstance(testcase, dict):
            relate_case_id = testcase['case_id']
            if relate_case_id not in str(all_case_id):
                raise ValueError('未在测试用例中找到关联测试用例，请检查关联测试用例的 case_id')
        elif isinstance(testcase, str):
            if testcase not in str(all_case_id):
                raise ValueError('未在测试用例中找到关联测试用例，请检查关联测试用例的 case_id')

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
                    if isinstance(case_data_test_steps, list):
                        for case_test_steps in case_data_test_steps:
                            if relate_case_id == case_test_steps['case_id']:
                                # 使命名更清晰
                                relate_case_steps = case_test_steps
                                # 避免循环关联
                                is_circular_relate(parsed.case_id, relate_case_steps)
                                # 重新组合测试用例
                                new_data = {
                                    'test_steps': relate_case_steps,
                                    'set_var_key': testcase['key'],
                                    'set_var_jsonpath': testcase['jsonpath']
                                }
                                case_data.update(new_data)
                                relate_testcase_set_var(case_data)
                    else:
                        relate_case_steps = case_data_test_steps
                        is_circular_relate(parsed.case_id, relate_case_steps)
                        new_data = {
                            'set_var_key': testcase['key'],
                            'set_var_jsonpath': testcase['jsonpath']
                        }
                        case_data.update(new_data)
                        relate_testcase_set_var(case_data)
            # 用例中 testcase 参数为直接关联测试用例时
            elif isinstance(testcase, str):
                if testcase in str(case_id_list):
                    if isinstance(case_data_test_steps, list):
                        for case_test_steps in case_data_test_steps:
                            if testcase == case_test_steps['case_id']:
                                relate_case_steps = case_test_steps
                                is_circular_relate(parsed.case_id, relate_case_steps)
                                new_data = {'test_steps': relate_case_steps}
                                case_data.update(new_data)
                                relate_testcase_exec(case_data)
                    else:
                        relate_case_steps = case_data_test_steps
                        is_circular_relate(parsed.case_id, relate_case_steps)
                        relate_testcase_exec(case_data)

    # 再次解析请求数据，应用关联测试用例设置的变量到请求数据
    parsed.request_data = VarsExtractor().relate_vars_replace(parsed.request_data)


def is_circular_relate(current_case_id: str, relate_case_steps: dict) -> NoReturn:
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
                        raise ValueError(
                            '关联测试用例执行失败，因为在关联测试用例中的关联测试用例参数内含有'
                            '当前正在执行的测试用例，导致了循环引用，触发此异常'
                        )
                else:
                    if current_case_id == relate_testcase:
                        raise ValueError(
                            '关联测试用例执行失败，因为在关联测试用例中的关联测试用例参数内含有'
                            '当前正在执行的测试用例，导致了循环引用，触发此异常'
                        )


def relate_testcase_set_var(testcase_data: dict) -> NoReturn:
    """
    关联测试用例设置变量

    :param testcase_data:
    :return:
    """
    from fastpt.common.send_request import send_request
    msg = '执行变量提取关联测试用例：{}'.format(testcase_data['test_steps']['case_id'])
    log.debug(msg)
    allure_step(msg)
    response = send_request.send_request(testcase_data, log_data=False)
    value = jsonpath(response, testcase_data['set_var_jsonpath'])
    if value:
        VariableCache().set(testcase_data['set_var_key'], value[0])
    else:
        raise ValueError('jsonpath 取值失败，表达式: {}'.format(testcase_data['set_var_jsonpath']))


def relate_testcase_exec(testcase_data: dict) -> NoReturn:
    """
    关联测试用例执行

    :param testcase_data:
    :return:
    """
    from fastpt.common.send_request import send_request
    msg = '执行关联测试用例：{}'.format(testcase_data['test_steps']['case_id'])
    log.debug(msg)
    allure_step(msg)
    send_request.send_request(testcase_data, log_data=False)
