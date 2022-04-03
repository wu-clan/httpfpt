#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from dirty_equals import IsInt

from fastpt.common.excel_operate import write_excel_report
from fastpt.common.log import log
from fastpt.common.send_request import send_request
from fastpt.common.yaml_operate import write_yaml_report
from fastpt.utils.parametrize_set import req_args, serialize_req_args, param_ids, req_values

excel_data = req_values(filename='APITestCaseTEMPLATE.xlsx')
yaml_data = req_values(filename='APITestCaseTEMPLATE.yaml')


class TestDemo:
    """ Demo """

    # 声明全局参数
    args = req_args()
    excel_ids = param_ids(excel_data)
    yaml_ids = param_ids(yaml_data)

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
    @pytest.mark.parametrize(args, excel_data, ids=excel_ids)
    def test_003(self, model, ID, UseCase, method, url, params, headers, body, body_type, status_code, msg, result,
                 tester):
        """ 测试003 """
        data = serialize_req_args(model, ID, UseCase, method, url, params, headers, body, body_type, status_code, msg,
                                  result, tester)
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
    @pytest.mark.parametrize(args, yaml_data, ids=yaml_ids)
    def test_004(self, model, ID, UseCase, method, url, params, headers, body, body_type, status_code, msg, result,
                 tester):
        """ 测试004 """
        data = serialize_req_args(model, ID, UseCase, method, url, params, headers, body, body_type, status_code, msg,
                                  result, tester)
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
