#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import allure
import pytest
from dirty_equals import IsInt

from fastpt.common.excel_operate import write_excel_report, read_excel, get_excel_row
from fastpt.common.log import log
from fastpt.common.send_request import send_request
from fastpt.common.yaml_operate import write_yaml_report, read_yaml
from fastpt.utils.assert_control import Asserter
from fastpt.utils.request.ids_extract import get_ids

excel_data = read_excel(filename='APITestCaseTEMPLATE.xlsx')
yaml_data = read_yaml(filename='APITestCaseTEMPLATE.yaml')


@allure.epic("demo接口")
@allure.feature("demo模块")
class TestDemo:
    """ Demo """

    # 声明参数
    excel_ids = get_ids(excel_data)
    yaml_ids = get_ids(yaml_data)

    @allure.story("简单输出")
    @pytest.mark.test_mark
    @pytest.mark.parametrize('a, b', [(1, 2)])
    def test_001(self, a, b):
        """ 测试001 """
        log.info("This is a demo's test")
        assert a != b

    @allure.story("xfall输出")
    @pytest.mark.xfail
    @pytest.mark.test_mark
    def test_002(self):
        """ 测试002 """
        log.info(f"这是一个框架xfail修饰测试")
        assert 1 == IsInt

    @allure.story("excel数据测试输出")
    @pytest.mark.test_api
    @pytest.mark.parametrize('data', excel_data, ids=excel_ids)
    def test_003(self, data):
        """ 测试003 """
        response = send_request.send_request(data)
        rs = response['status_code']
        # excel 测试报告需手动写入
        # 条件自定义, 但是对 用例id 要求严格, 请注意查看使用说明
        row_num = get_excel_row(data)
        if rs == 200:
            write_excel_report(row_num=row_num, status='pass')
        else:
            write_excel_report(row_num=row_num, status='fail')
        # 请求数据中包含非常规字符串内容时, 强烈建议使用请求响应数据, 应为解析后的接口请求数据也包含在内
        Asserter().exec_asserter(response, assert_text=response['request_data']['assert'])

    @allure.story("yaml数据测试输出")
    @pytest.mark.test_api
    @pytest.mark.parametrize('data', yaml_data, ids=yaml_ids)
    def test_004(self, data):
        """ 测试004 """
        response = send_request.send_request(data)
        rs = response['status_code']
        # yaml 测试报告需要手动写入
        # 条件, 写入内容均可自定义
        if rs == 200:
            write_yaml_report(data=[{'case': data['case_id'], 'result': 'PASS'}], status='pass')
        else:
            write_yaml_report(data=[{'case': data['case_id'], 'result': 'FAIL'}], status='fail')
        Asserter().exec_asserter(response, assert_text=response['request_data']['assert'])
