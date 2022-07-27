#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import datetime
import json
import time
from json import JSONDecodeError

import allure
import httpx
import requests
from httpx import Response as HttpxResponse
from requests import Response as RequestsResponse

from fastpt.common.log import log
from fastpt.core import get_conf
from fastpt.db.mysql_db import DB
from fastpt.utils.allure_operate import allure_attach_file, allure_step
from fastpt.utils.request.data_parse import DataParse
from fastpt.utils.time_control import get_current_time


class SendRequests:
    """ 发送请求 """

    def __init__(self, ):
        self.request_engin_list = [
            'requests',
            'httpx'
        ]

    @property
    def init_response_meta_data(self) -> dict:
        """
        :return: 响应元数据
        """
        response_meta_data = {
            "request_data": {
                "module": None,
                "case_id": None,
                "case_desc": None,
                "method": None,
                "params": None,
                "data_type": None,
                "data": None,
                "files": None,
                "sql": None,
                "assert": None,
            },
            "url": None,
            "status_code": 200,
            "elapsed": 0,
            "headers": None,
            "cookies": None,
            "result": None,
            "content": None,
            "text": None,
            "stat": {
                "execute_time": None,
            },
            "sql_data": None
        }
        return response_meta_data

    @staticmethod
    def _requests_engin(**kwargs) -> RequestsResponse:
        """
        requests 引擎

        :param kwargs:
        :return:
        """
        try:
            # 消除安全警告
            requests.packages.urllib3.disable_warnings()  # noqa
            # 请求间隔
            time.sleep(get_conf.REQUEST_INTERVAL)
            log.info('开始发送请求...')
            response = requests.session().request(
                timeout=get_conf.REQUEST_TIMEOUT,
                verify=get_conf.REQUEST_VERIFY,
                proxies=get_conf.REQUEST_PROXIES_REQUESTS,
                **kwargs
            )
            return response
        except Exception as e:
            log.error(f'请求异常: {e}')
            raise e

    @staticmethod
    def _httpx_engin(**kwargs) -> HttpxResponse:
        """
        httpx 引擎

        :param kwargs:
        :return:
        """
        try:
            # 请求间隔
            time.sleep(get_conf.REQUEST_INTERVAL)
            log.info('开始发送请求...')
            with httpx.Client(
                    verify=get_conf.REQUEST_VERIFY,
                    proxies=get_conf.REQUEST_PROXIES_HTTPX,
                    follow_redirects=True,
            ) as client:
                response = client.request(
                    timeout=get_conf.REQUEST_TIMEOUT,
                    **kwargs
                )
                return response
        except Exception as e:
            log.error(f'请求异常: {e}')
            raise e

    def send_request(self, data: dict, *, request_engin: str = 'requests', **kwargs):
        """
        发送请求

        :param data: 请求数据
        :param request_engin: 请求引擎
        :return: response
        """
        if request_engin not in self.request_engin_list:
            raise ValueError(f'请求发起失败，请使用正确的请求引擎')
        # 获取解析后的请求数据
        parsed_data = DataParse(data)
        # 初始化响应元数据
        response_data = self.init_response_meta_data
        # 日志记录请求数据
        self.log_request_up(parsed_data)
        self.allure_request_up(parsed_data)
        # 执行时间
        execute_time = get_current_time()
        response_data['stat']['execute_time'] = execute_time
        response = None
        if request_engin == 'requests':
            response = self._requests_engin(**parsed_data.get_request_args_parsed, **kwargs)
        elif request_engin == 'httpx':
            response = self._httpx_engin(**parsed_data.get_request_args_parsed, **kwargs)
        # 后置 sql
        if parsed_data.sql:
            sql_data = DB().exec_case_sql(parsed_data.sql)
        else:
            sql_data = parsed_data.sql
        # 记录请求数据
        response_data['request_data']['module'] = parsed_data.url
        response_data['request_data']['case_id'] = parsed_data.case_id
        response_data['request_data']['case_desc'] = parsed_data.case_desc
        response_data['request_data']['method'] = parsed_data.method
        response_data['request_data']['params'] = parsed_data.params
        response_data['request_data']['data_type'] = parsed_data.data_type
        response_data['request_data']['data'] = parsed_data.data
        response_data['request_data']['files'] = parsed_data.files
        response_data['request_data']['sql'] = parsed_data.sql
        response_data['request_data']['assert'] = parsed_data.assert_text
        # 记录响应数据
        response_data['url'] = str(response.url)
        response_data['status_code'] = int(response.status_code)
        response_data['elapsed'] = response.elapsed.microseconds / 1000.0
        response_data['headers'] = response.headers
        response_data['cookies'] = dict(response.cookies)
        try:
            json_data = response.json()
        except JSONDecodeError:
            json_data = {}
        response_data['result'] = json.dumps(json_data)
        response_data['content'] = response.content.decode('utf-8')
        response_data['text'] = response.text
        response_data['sql_data'] = sql_data
        # 响应日志记录
        self.log_request_down(response_data)

        return response_data

    @staticmethod
    def log_request_up(parsed: DataParse):
        log.info(f"用例 module: {parsed.module}")
        log.info(f"用例 case_id: {parsed.case_id}")
        log.info(f"请求 method: {parsed.method}")
        log.info(f"请求 url: {parsed.url}")
        log.info(f"请求 params: {parsed.params}")
        log.info(f'请求 headers: {parsed.headers}')
        log.info(f"请求 data 类型：{parsed.data_type}")
        if parsed.data_type != 'json':
            log.info(f"请求 data：{parsed.data}")
        else:
            log.info(f"请求 json: {parsed.data}")
        log.info(f"请求 sql: {parsed.sql}")
        log.info(f"请求 files: {parsed.files_no_parse}")
        log.info(f"请求 assert: {parsed.assert_text}")

    @staticmethod
    def log_request_down(response_data: dict):
        log.info(f"请求发送时间: {response_data['stat']['execute_time']}")
        log.info(f"响应状态码: {response_data['status_code']}")
        log.info(f"响应时间: {response_data['elapsed']} ms")

    @staticmethod
    def allure_request_up(parsed: DataParse):
        allure.dynamic.title(
            f"用例 module: {parsed.module};"
            f"用例 case_id: {parsed.case_id}"
        )
        allure.dynamic.description(parsed.case_desc) if parsed.case_desc else ...
        allure_step(f"请求 method: {parsed.method}")
        allure.dynamic.link(parsed.url)
        allure_step(f"请求 params: {parsed.params}")
        allure_step(f'请求 headers: {parsed.headers}')
        allure_step(f"请求 data 类型：{parsed.data_type}")
        if parsed.data_type != 'json':
            allure_step(f"请求 data：{parsed.data}")
        else:
            allure_step(f"请求 json: {parsed.data}")
        allure_step(f"请求 sql: {parsed.sql}")
        if parsed.files_no_parse is not None:
            for k, v in parsed.files_no_parse.items():
                if isinstance(v, list):
                    for path in v:
                        allure_attach_file(path)
                else:
                    allure_attach_file(parsed.files_no_parse)
        allure_step(f"请求 assert: {parsed.assert_text}")


send_request = SendRequests()
