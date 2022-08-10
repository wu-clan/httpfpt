#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from jsonpath import jsonpath

from fastpt.common.log import log
from fastpt.common.variable_cache import VariableCache
from fastpt.common.yaml_handler import read_yaml
from fastpt.utils.file_control import search_all_case_yaml_files
from fastpt.utils.request.request_data_parse import RequestDataParse
from fastpt.utils.request.vars_extractor import VarsExtractor


def exec_setup_testcase(parsed: RequestDataParse, setup_testcase: list) -> dict:
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

    # 获取所有测试用例数据
    all_yaml_file = search_all_case_yaml_files()
    all_case_data = []
    for file in all_yaml_file:
        read_data = read_yaml(None, filename=file)
        all_case_data.append(read_data)

    # 判断是否含有关联测试用例
    all_case_id = []
    for case_data in all_case_data:
        steps = case_data['test_steps']
        if isinstance(steps, list):
            for i in steps:
                all_case_id.append(i['case_id'])
        else:
            all_case_id.append(steps['case_id'])
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
            elif isinstance(testcase, str):
                # testcase 就是 relate_case_id
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


def relate_testcase_set_var(testcase_data: dict) -> None:
    """
    关联测试用例设置变量

    :param testcase_data:
    :return:
    """
    from fastpt.common.send_request import send_request
    log.info('执行变量提取关联测试用例：{}'.format(testcase_data['test_steps']['case_id']))
    response = send_request.send_request(testcase_data, log_data=False)
    value = jsonpath(response, testcase_data['set_var_jsonpath'])
    if value:
        VariableCache().set(testcase_data['set_var_key'], value[0])
    else:
        raise ValueError('jsonpath 取值失败，表达式: {}'.format(testcase_data['set_var_jsonpath']))


def relate_testcase_exec(testcase_data: dict) -> None:
    """
    关联测试用例执行

    :param testcase_data:
    :return:
    """
    from fastpt.common.send_request import send_request
    log.info('执行关联测试用例：{}'.format(testcase_data['test_steps']['case_id']))
    send_request.send_request(testcase_data, log_data=False)
