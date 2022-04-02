#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastpt.common.excel_operate import write_excel_report
from fastpt.common.log import log
from fastpt.common.yaml_operate import write_yaml_report


def fast_excel_report(file, row_num, status) -> None:
    """
    快速创建excel测试报告
    :param file: excel测试数据文件名
    :param row_num: 写入excel报告文件数据所在行
    :param status: 写入excel报告测试结果
    :return:
    """
    if status == 'PASS':
        log.success(f"test result: ----> {status}")
        write_excel_report(datafile=file, row_n=row_num, status=status)
    else:
        raise ValueError('参数 status 只能为 "PASS" or "FAIL"')
    if status == 'FAIL':
        log.error(f"test result: ----> {status}")
        write_excel_report(datafile=file, row_n=row_num, status=status)
    else:
        raise ValueError('参数 status 只能为 "PASS" or "FAIL"')


def fast_yaml_report(data, status, result) -> None:
    """
    快速创建yaml测试报告
    :param data: 写入数据
    :param status: 写入yaml报告测试结果
    :param result: 请求响应信息
    :return:
    """
    if status == 'PASS':
        log.success(f"test result: ----> PASS")
        write_yaml_report(data=[{status: {'request': data, 'response': result}}])
    else:
        raise ValueError('参数 status 只能为 "PASS" or "FAIL"')
    if status == 'FAIL':
        log.error(f"test result: ----> FAIL")
        write_yaml_report(data=[{status: {'request': data, 'response': result}}])
    else:
        raise ValueError('参数 status 只能为 "PASS" or "FAIL"')
