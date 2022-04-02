#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from dirty_equals import IsInt

from fastpt.common.excel_operate import read_excel, write_excel_report
from fastpt.common.log import log
from fastpt.common.send_request import send_request
from fastpt.common.yaml_operate import read_yaml, write_yaml_report
from fastpt.utils.fast_file_report import fast_excel_report, fast_yaml_report

excel_data = read_excel(filename='APITestCaseTEMPLATE.xlsx')
yaml_data = read_yaml(filename='APITestCaseTEMPLATE.yaml')


class TestDemo:
    req_args = ['ID', 'method', 'url', 'params', 'headers', 'body', 'status_code', 'msg']

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
        # log.info(f"这是一个框架普通测试")
        log.info(excel_data)
        log.info(yaml_data)
        # 这两个断言情况是相同的
        # 请查看: https://dirty-equals.helpmanual.io/
        assert 1 == IsInt
        assert 1 != ~IsInt

    @pytest.mark.test_api
    @pytest.mark.parametrize(req_args, *excel_data)
    def test_003(self, ID, method, url, params, headers, body, status_code, msg):
        """ 测试003 """
        data = {'ID': ID, 'method': method, 'url': url, 'params': params, 'headers': headers, 'body': body, 'msg': msg,
                'status_code': status_code}
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
            fast_excel_report('APITestCaseTEMPLATE.xlsx', row_num, status)
        if read_code != code or read_msg != msg:
            status = 'FAIL'
            fast_excel_report('APITestCaseTEMPLATE.xlsx', row_num, status)
        assert code == read_code, "返回实际结果是->: %s" % code
        assert msg == read_msg, "返回实际结果是->: %s" % msg

    @pytest.mark.test_api
    @pytest.mark.parametrize(req_args, *yaml_data)
    def test_004(self, ID, method, url, params, headers, body, status_code, msg):
        """ 测试004 """
        data = {'ID': ID, 'method': method, 'url': url, 'params': params, 'headers': headers, 'body': body, 'msg': msg,
                'status_code': status_code}
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
            fast_yaml_report(data, status, result)
        if read_code != code or read_msg != msg:
            status = 'FAIL'
            fast_yaml_report(data, status, result)
        assert code == read_code, "返回实际结果是->: %s" % code
        assert msg == read_msg, "返回实际结果是->: %s" % msg
