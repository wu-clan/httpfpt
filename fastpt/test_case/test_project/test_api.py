#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import allure
import pytest
from dirty_equals import IsInt

from fastpt.common.log import log
from fastpt.common.send_request import send_request
from fastpt.common.yaml_handler import write_yaml_report, read_yaml
from fastpt.utils.request.file_data_parse import get_request_data
from fastpt.utils.request.ids_extract import get_ids

# excel_data = get_request_data(read_excel(filename='APITestCaseTEMPLATE.xlsx'))
yaml_data = get_request_data(read_yaml(filename='APITestCaseTEMPLATE.yaml'))


@allure.epic(yaml_data[0]['config']['allure']['epic'])
@allure.feature(yaml_data[0]['config']['allure']['feature'])
class TestDemo:
    """ Demo """

    # 声明参数
    # excel_ids = get_ids(excel_data)
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

    # @allure.story("excel数据测试输出")
    # @pytest.mark.test_api
    # @pytest.mark.parametrize('data', excel_data, ids=excel_ids)
    # def test_003(self, data):
    #     """ 测试003 """
    #     response = send_request.send_request(data)
    #     rs = response['status_code']
    #     # excel 测试报告需手动写入
    #     # 条件自定义, 但是对 用例id 要求严格, 请注意查看使用说明
    #     row_num = get_excel_row(data)
    #     if rs == 200:
    #         write_excel_report(row_num=row_num, status='pass')
    #     else:
    #         write_excel_report(row_num=row_num, status='fail')

    @allure.story(yaml_data[0]['config']['allure']['story'])
    @pytest.mark.test_api
    @pytest.mark.parametrize('data', yaml_data, ids=yaml_ids)
    def test_004(self, data):
        """ 测试004 """
        response = send_request.send_request(data)
        if response:
            write_yaml_report(data=[{'case': data['test_steps']['case_id'], 'result': 'FAIL'}], status='fail')
        else:
            write_yaml_report(data=[{'case': data['test_steps']['case_id'], 'result': 'PASS'}], status='pass')



