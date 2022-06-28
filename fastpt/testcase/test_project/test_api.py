#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from dirty_equals import IsInt

from fastpt.common.excel_operate import write_excel_report, read_excel
from fastpt.common.log import log
from fastpt.common.send_request import send_request
from fastpt.common.yaml_operate import write_yaml_report, read_yaml
from fastpt.utils.data_extraction import get_ids

excel_data = read_excel(filename='APITestCaseTEMPLATE.xlsx')
yaml_data = read_yaml(filename='APITestCaseTEMPLATE.yaml')


class TestDemo:
    """ Demo """

    # 声明全局参数
    excel_ids = get_ids(excel_data)
    yaml_ids = get_ids(yaml_data)

    @pytest.mark.test_mark
    @pytest.mark.parametrize('a, b', [(1, 2)])
    def test_001(self, a, b):
        """ 测试001 """
        log.info("This is a frame's test")
        assert a != b

    @pytest.mark.xfail
    @pytest.mark.test_mark
    def test_002(self):
        """ 测试002 """
        log.info(f"这是一个框架xfail修饰测试")
        # 这两个断言情况是相同的
        # 请查看: https://dirty-equals.helpmanual.io/
        assert 1 == IsInt
        assert 1 != ~IsInt

    @pytest.mark.test_api
    @pytest.mark.parametrize('data', excel_data, ids=excel_ids)
    def test_003(self, data):
        """ 测试003 """
        row_num = int(data['ID'].split("_")[2]) + 1
        req = send_request.send_requests(data)
        # 获取服务端返回的值
        result = req.json()
        code = int(result['code'])
        msg = str(result['msg'])
        log.info("response：%s" % req.content.decode("utf-8"))
        # 获取excel表格数据的状态码和消息
        read_code = int(data["status_code"])
        read_msg = data["msg"]
        if read_code == code and read_msg == msg:
            status = 'PASS'
            write_excel_report('APITestCaseTEMPLATE.xlsx', row_num=row_num, status=status)
        if read_code != code or read_msg != msg:
            status = 'FAIL'
            write_excel_report('APITestCaseTEMPLATE.xlsx', row_num=row_num, status=status)
        assert code == read_code, "返回实际结果是->: %s" % code
        assert msg == read_msg, "返回实际结果是->: %s" % msg

    @pytest.mark.test_api
    @pytest.mark.parametrize('data', yaml_data, ids=yaml_ids)
    def test_004(self, data):
        """ 测试004 """
        req = send_request.send_httpx(data)
        # 获取服务端返回的值
        result = req.json()
        code = int(result['code'])
        msg = str(result['msg'])
        log.info("response：%s" % req.content.decode("utf-8"))
        # 获取excel表格数据的状态码和消息
        read_code = int(data["status_code"])
        read_msg = data["msg"]
        if read_code == code and read_msg == msg:
            status = 'PASS'
            write_yaml_report(data=[{status: {'request': data, 'response': result}}], status=status)
        if read_code != code or read_msg != msg:
            status = 'FAIL'
            write_yaml_report(data=[{status: {'request': data, 'response': result}}], status=status)
        assert code == read_code, "返回实际结果是->: %s" % code
        assert msg == read_msg, "返回实际结果是->: %s" % msg
