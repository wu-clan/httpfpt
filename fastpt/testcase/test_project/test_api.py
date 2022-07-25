#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import allure
import pytest
from dirty_equals import IsInt

from fastpt.common.excel_operate import write_excel_report, read_excel, get_excel_row
from fastpt.common.log import log
from fastpt.common.send_request import send_request
from fastpt.common.yaml_operate import write_yaml_report, read_yaml
from fastpt.utils.request.ids_extract import get_ids

excel_data = read_excel(filename='APITestCaseTEMPLATE.xlsx')
yaml_data = read_yaml(filename='APITestCaseTEMPLATE.yaml')


@allure.epic("demo接口")
@allure.feature("demo模块")
class TestDemo:
    """ Demo """

    # 声明全局参数
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
        # 这两个断言情况是相同的
        # 请查看: https://dirty-equals.helpmanual.io/
        assert 1 == IsInt
        assert 1 != ~IsInt

    @allure.story("excel数据测试输出")
    @pytest.mark.test_api
    @pytest.mark.parametrize('data', excel_data, ids=excel_ids)
    def test_003(self, data):
        """ 测试003 """
        row_num = get_excel_row(data)
        rp = send_request.send_request(data)
        rs = rp['status_code']
        if rs == 200:
            write_excel_report(row_num=row_num, status='pass')
        else:
            write_excel_report(row_num=row_num, status='fail')
        assert rs == 200, "返回实际结果是->: %s" % rs  # 暂时的

    @allure.story("yaml数据测试输出")
    @pytest.mark.test_api
    @pytest.mark.parametrize('data', yaml_data, ids=yaml_ids)
    def test_004(self, data):
        """ 测试004 """
        rp = send_request.send_request(data)
        rs = rp['status_code']
        if rs == 200:
            status = 'PASS'
            write_yaml_report(data=[{'case': data['case_id'], 'result': status}], status=status)
        else:
            status = 'FAIL'
            write_yaml_report(data=[{'case': data['case_id'], 'result': status}], status=status)
        assert rs == 200, "返回实际结果是->: %s" % rs  # 暂时的
