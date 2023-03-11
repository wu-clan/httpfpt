#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import json
import time
from json import JSONDecodeError
from typing import NoReturn

import allure
import httpx
import requests
from httpx import Response as HttpxResponse
from requests import Response as RequestsResponse

from fastpt.common.log import log
from fastpt.core import get_conf
from fastpt.db.mysql_db import MysqlDB
from fastpt.enums.request.body import BodyType
from fastpt.enums.request.engin import EnginType
from fastpt.utils.allure_control import allure_attach_file
from fastpt.utils.assert_control import Asserter
from fastpt.utils.enum_control import get_enum_values
from fastpt.utils.relate_testcase_executor import exec_setup_testcase
from fastpt.utils.request.hooks_executor import HookExecutor
from fastpt.utils.request.request_data_parse import RequestDataParse
from fastpt.utils.request.vars_extractor import VarsExtractor
from fastpt.utils.time_control import get_current_time


class SendRequests:
    """ 发送请求 """

    @property
    def init_response_meta_data(self) -> dict:
        """
        :return: 响应元数据
        """
        response_meta_data = {
            "url": None,
            "status_code": 200,
            "elapsed": 0,
            "headers": None,
            "cookies": None,
            "json": None,
            "content": None,
            "text": None,
            "stat": {
                "execute_time": None,
            }
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
            kwargs['timeout'] = kwargs['timeout'] or get_conf.REQUEST_TIMEOUT
            kwargs['verify'] = kwargs['verify'] or get_conf.REQUEST_VERIFY
            kwargs['proxies'] = kwargs['proxies'] or get_conf.REQUEST_PROXIES_REQUESTS
            kwargs['allow_redirects'] = kwargs['allow_redirects'] or get_conf.REQUEST_REDIRECTS
            # 消除安全警告
            requests.packages.urllib3.disable_warnings()  # noqa
            log.info('开始发送请求...')
            response = requests.session().request(**kwargs)
            return response
        except Exception as e:
            log.error(f'发送 requests 请求异常: {e}')
            raise e

    @staticmethod
    def _httpx_engin(**kwargs) -> HttpxResponse:
        """
        httpx 引擎

        :param kwargs:
        :return:
        """
        try:
            kwargs['timeout'] = kwargs['timeout'] or get_conf.REQUEST_TIMEOUT
            verify = kwargs['verify'] or get_conf.REQUEST_VERIFY
            proxies = kwargs['proxies'] or get_conf.REQUEST_PROXIES_HTTPX
            redirects = kwargs['allow_redirects'] or get_conf.REQUEST_REDIRECTS
            del kwargs['verify']
            del kwargs['proxies']
            del kwargs['allow_redirects']
            log.info('开始发送请求...')
            with httpx.Client(
                    verify=verify,
                    proxies=proxies,
                    follow_redirects=redirects,
            ) as client:
                response = client.request(**kwargs)
                return response
        except Exception as e:
            log.error(f'发送 httpx 请求异常: {e}')
            raise e

    def send_request(
            self,
            request_data: dict,
            *,
            request_engin: str = 'requests',
            log_data: bool = True,
            **kwargs
    ) -> dict:
        """
        发送请求

        :param request_data: 请求数据
        :param request_engin: 请求引擎
        :param log_data: 日志记录数据
        :return: response
        """
        if request_engin not in get_enum_values(EnginType):
            raise ValueError(f'请求发起失败，请使用合法的请求引擎')

        # 获取解析后的请求数据
        log.info('开始解析请求数据')
        parsed_data = RequestDataParse(request_data, request_engin)
        log.info('请求数据解析完成')

        # 日志记录前置请求日志
        if log_data:
            self.log_request_setup(parsed_data)

        # 前置处理
        if parsed_data.is_setup:
            log.info('开始处理请求前置...')
            try:
                setup_testcase = parsed_data.setup_testcase
                if setup_testcase is not None:
                    exec_setup_testcase(parsed_data, setup_testcase)
                setup_sql = parsed_data.setup_sql
                if setup_sql is not None:
                    MysqlDB().exec_case_sql(setup_sql, parsed_data.env)
                setup_hooks = parsed_data.setup_hooks
                if setup_hooks is not None:
                    HookExecutor().exec_case_func(setup_hooks)
                wait_time = parsed_data.setup_wait_time
                if wait_time is not None:
                    log.info(f'执行请求前等待：{wait_time} s')
                    time.sleep(wait_time)
            except Exception as e:
                log.error(f'请求前置处理异常: {e}')
                raise e
            log.info('请求前置处理完成')

        # 日志记录请求数据
        if log_data:
            self.log_request_up(parsed_data)

        # allure 记录请求数据
        self.allure_request_up(parsed_data)

        # 发送请求
        request_conf = {
            'timeout': parsed_data.timeout,
            'verify': parsed_data.verify,
            'proxies': parsed_data.proxies,
            'allow_redirects': parsed_data.redirects,
        }
        response_data = self.init_response_meta_data
        response_data['stat']['execute_time'] = get_current_time()
        if request_engin == EnginType.requests:
            response = self._requests_engin(
                **request_conf,
                **parsed_data.get_request_data_parsed,
                **kwargs
            )
        elif request_engin == EnginType.httpx:
            response = self._httpx_engin(
                **request_conf,
                **parsed_data.get_request_data_parsed,
                **kwargs
            )
        else:
            raise ValueError(f'请求发起失败，使用了不合法的请求引擎')

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
        response_data['json'] = json.dumps(json_data)
        response_data['content'] = response.content.decode('utf-8')
        response_data['text'] = response.text

        # 日志记录响应
        if log_data:
            self.log_request_down(response_data)
            self.log_request_teardown(parsed_data)

        # 后置处理
        if parsed_data.is_teardown:
            log.info('开始处理请求后置...')
            try:
                teardown_sql = parsed_data.teardown_sql
                if teardown_sql is not None:
                    MysqlDB().exec_case_sql(teardown_sql, parsed_data.env)
                teardown_hooks = parsed_data.teardown_hooks
                if teardown_hooks is not None:
                    HookExecutor().exec_case_func(teardown_hooks)
                teardown_extract = parsed_data.teardown_extract
                if teardown_extract is not None:
                    VarsExtractor().teardown_var_extract(response_data, teardown_extract, parsed_data.env)
                teardown_assert = parsed_data.teardown_assert
                if teardown_assert is not None:
                    Asserter().exec_asserter(response_data, assert_text=teardown_assert)
                wait_time = parsed_data.teardown_wait_time
                if wait_time is not None:
                    log.info(f'执行请求后等待：{wait_time} s')
                    time.sleep(wait_time)
            except Exception as e:
                log.error(f'请求后置处理异常: {e}')
                raise e
            log.info('请求后置处理完成')

        return response_data

    @staticmethod
    def log_request_setup(parsed: RequestDataParse) -> NoReturn:
        log.info(f'请求 setup_testcase: {parsed.setup_testcase}')
        log.info(f"请求 setup_sql: {parsed.setup_sql}")
        log.info(f"请求 setup_hooks: {parsed.setup_hooks}")
        log.info(f"请求 setup_wait_time: {parsed.setup_wait_time}")

    @staticmethod
    def log_request_up(parsed: RequestDataParse) -> NoReturn:
        log.info(f"用例 env: {parsed.env}")
        log.info(f"用例 module: {parsed.module}")
        log.info(f"用例 name: {parsed.name}")
        log.info(f"用例 case_id: {parsed.case_id}")
        log.info(f"用例 description: {parsed.description}")
        log.info(f"请求 method: {parsed.method}")
        log.info(f"请求 url: {parsed.url}")
        log.info(f"请求 params: {parsed.params}")
        log.info(f'请求 headers: {parsed.headers}')
        log.info(f"请求 data_type：{parsed.body_type}")
        if parsed.body_type != BodyType.JSON.value:
            log.info(f"请求 data：{parsed.body}")
        else:
            log.info(f"请求 json: {parsed.body}")
        log.info(f"请求 files: {parsed.files_no_parse}")

    @staticmethod
    def log_request_teardown(parsed: RequestDataParse) -> NoReturn:
        log.info(f"请求 teardown_sql: {parsed.teardown_sql}")
        log.info(f"请求 teardown_extract: {parsed.teardown_extract}")
        log.info(f"请求 teardown_assert: {parsed.teardown_assert}")
        log.info(f"请求 teardown_wait_time: {parsed.teardown_wait_time}")

    @staticmethod
    def log_request_down(response_data: dict) -> NoReturn:
        log.info(f"请求发送时间: {response_data['stat']['execute_time']}")
        str_status_code = str(response_data['status_code'])
        if str_status_code.startswith('4') or str_status_code.startswith('5'):
            log.error(f"响应状态码: {response_data['status_code']}")
        else:
            log.success(f"响应状态码: {response_data['status_code']}")
        log.info(f"响应时间: {response_data['elapsed']} ms")

    @staticmethod
    def allure_request_up(parsed: RequestDataParse) -> NoReturn:
        allure.dynamic.title(f"用例 case_id: {parsed.case_id}")
        allure.dynamic.description(parsed.description)
        allure.dynamic.link(parsed.url)
        if parsed.files_no_parse is not None:
            for k, v in parsed.files_no_parse.items():
                if isinstance(v, list):
                    for path in v:
                        allure_attach_file(path)
                else:
                    allure_attach_file(v)


send_request = SendRequests()
