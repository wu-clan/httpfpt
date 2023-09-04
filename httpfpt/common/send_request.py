#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import json
import time
from json import JSONDecodeError
from typing import Literal

import allure
import httpx
import requests
from httpx import Response as HttpxResponse
from requests import Response as RequestsResponse

from httpfpt.common.log import log
from httpfpt.core import get_conf
from httpfpt.db.mysql_db import MysqlDB
from httpfpt.enums.request.body import BodyType
from httpfpt.enums.request.engin import EnginType
from httpfpt.utils.allure_control import allure_attach_file, allure_step
from httpfpt.utils.assert_control import Asserter
from httpfpt.utils.enum_control import get_enum_values
from httpfpt.utils.relate_testcase_executor import exec_setup_testcase
from httpfpt.utils.request.hooks_executor import HookExecutor
from httpfpt.utils.request.request_data_parse import RequestDataParse
from httpfpt.utils.request.vars_extractor import VarsExtractor
from httpfpt.utils.time_control import get_current_time


class SendRequests:
    """发送请求"""

    @property
    def init_response_metadata(self) -> dict:
        """
        :return: 响应元数据
        """
        response_metadata = {
            'url': None,
            'status_code': 200,
            'elapsed': 0,
            'headers': None,
            'cookies': None,
            'json': None,
            'content': None,
            'text': None,
            'stat': {
                'execute_time': None,
            },
        }
        return response_metadata

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
            requests.packages.urllib3.disable_warnings()  # type: ignore
            log.info('开始发送请求...')
            response = requests.session().request(**kwargs)
            response.raise_for_status()
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
                proxies=proxies,  # type: ignore
                follow_redirects=redirects,
            ) as client:
                response = client.request(**kwargs)
                response.raise_for_status()
                return response
        except Exception as e:
            log.error(f'发送 httpx 请求异常: {e}')
            raise e

    def send_request(
        self,
        request_data: dict,
        *,
        request_engin: Literal['requests', 'httpx'] = 'requests',
        log_data: bool = True,
        allure_data: bool = True,
        relate_testcase: bool = False,
        **kwargs,
    ) -> dict:
        """
        发送请求

        :param request_data: 请求数据
        :param request_engin: 请求引擎
        :param log_data: 日志记录数据
        :param allure_data: allure 记录数据
        :param relate_testcase: 关联测试用例
        :return: response
        """
        if request_engin not in get_enum_values(EnginType):
            raise ValueError('请求发起失败，请使用合法的请求引擎')

        # 获取解析后的请求数据
        log.info('开始解析请求数据')
        request_data_parse = RequestDataParse(request_data, request_engin)
        parsed_data = request_data_parse.get_request_data_parsed
        log.info('请求数据解析完成')
        if not relate_testcase:
            log.info(f'🏷️ Case ID: {parsed_data["case_id"]}')

        # 记录请求前置数据; 请注意: 此处数据中如果包含关联用例变量, 不会被替换为结果记录, 因为替换动作还未发生
        if log_data:
            self.log_request_setup(parsed_data)
        if allure_data:
            self.allure_request_setup(parsed_data)

        # 前置处理
        if parsed_data['is_setup']:
            log.info('开始处理请求前置...')
            try:
                setup_testcase = parsed_data['setup_testcase']
                if setup_testcase is not None:
                    new_parsed = exec_setup_testcase(request_data_parse, setup_testcase)
                    if isinstance(new_parsed, RequestDataParse):
                        # 对呀引用了关联测试用例变量的测试来讲, 这里可能造成微小的性能损耗
                        parsed_data = request_data_parse.get_request_data_parsed
                setup_sql = parsed_data['setup_sql']
                if setup_sql is not None:
                    MysqlDB().exec_case_sql(setup_sql, parsed_data['env'])
                setup_hooks = parsed_data['setup_hooks']
                if setup_hooks is not None:
                    HookExecutor().exec_hook_func(setup_hooks)
                wait_time = parsed_data['setup_wait_time']
                if wait_time is not None:
                    log.info(f'执行请求前等待：{wait_time} s')
                    time.sleep(wait_time)
            except Exception as e:
                log.error(f'请求前置处理异常: {e}')
                raise e
            log.info('请求前置处理完成')

        # 记录请求数据
        if log_data:
            self.log_request_up(parsed_data)
        if allure_data:
            self.allure_request_up(parsed_data)

        # allure 记录动态数据
        self.allure_dynamic_data(parsed_data)

        # 发送请求
        request_conf = {
            'timeout': parsed_data['timeout'],
            'verify': parsed_data['verify'],
            'proxies': parsed_data['proxies'],
            'allow_redirects': parsed_data['redirects'],
        }
        response_data = self.init_response_metadata
        request_data_parsed = {
            'method': parsed_data['method'],
            'url': parsed_data['url'],
            'params': parsed_data['params'],
            'headers': parsed_data['headers'],
            'data': parsed_data['body'],
            'files': parsed_data['files'],
        }
        if parsed_data['body_type'] == BodyType.JSON or parsed_data['body_type'] == BodyType.GraphQL:
            request_data_parsed.update({'json': request_data_parsed.pop('data')})
        elif parsed_data['body_type'] == BodyType.binary:
            if request_engin == EnginType.httpx:
                request_data_parsed.update({'content': request_data_parsed.pop('data')})
        response_data['stat']['execute_time'] = get_current_time()
        if request_engin == EnginType.requests:
            response = self._requests_engin(**request_conf, **request_data_parsed, **kwargs)
        elif request_engin == EnginType.httpx:
            response = self._httpx_engin(**request_conf, **request_data_parsed, **kwargs)
        else:
            raise ValueError('请求发起失败，请使用合法的请求引擎')

        # 记录响应数据
        response_data['url'] = str(response.url)
        response_data['status_code'] = int(response.status_code)
        response_data['elapsed'] = response.elapsed.microseconds / 1000.0
        response_data['headers'] = response.headers
        response_data['cookies'] = dict(response.cookies)
        try:
            json_data = response.json()
        except JSONDecodeError:
            log.warning('响应数据解析失败，响应数据不是有效的 json 格式')
            json_data = {}
        response_data['json'] = json.dumps(json_data)
        response_data['content'] = response.content.decode('utf-8')
        response_data['text'] = response.text

        # 记录响应数据
        if log_data:
            self.log_request_down(response_data)
            self.log_request_teardown(parsed_data)
        if allure_data:
            self.allure_request_down(response_data)
            self.allure_request_teardown(parsed_data)

        # 后置处理
        if parsed_data['is_teardown']:
            log.info('开始处理请求后置...')
            try:
                teardown_sql = parsed_data['teardown_sql']
                if teardown_sql is not None:
                    MysqlDB().exec_case_sql(teardown_sql, parsed_data['env'])
                teardown_hooks = parsed_data['teardown_hooks']
                if teardown_hooks is not None:
                    HookExecutor().exec_hook_func(teardown_hooks)
                teardown_extract = parsed_data['teardown_extract']
                if teardown_extract is not None:
                    VarsExtractor().teardown_var_extract(response_data, teardown_extract, parsed_data['env'])
                teardown_assert = parsed_data['teardown_assert']
                if teardown_assert is not None:
                    Asserter().exec_asserter(response_data, assert_text=teardown_assert)
                wait_time = parsed_data['teardown_wait_time']
                if wait_time is not None:
                    log.info(f'执行请求后等待：{wait_time} s')
                    time.sleep(wait_time)
            except AssertionError as e:
                log.error(f'断言失败: {e}')
                raise e
            except Exception as e:
                log.error(f'请求后置处理异常: {e}')
                raise e
            log.info('请求后置处理完成')

        return response_data

    @staticmethod
    def log_request_setup(parsed_data: dict) -> None:
        log.info(f"请求 setup_testcase: {parsed_data['setup_testcase']}")
        log.info(f"请求 setup_sql: {parsed_data['setup_sql']}")
        log.info(f"请求 setup_hooks: {parsed_data['setup_hooks']}")
        log.info(f"请求 setup_wait_time: {parsed_data['setup_wait_time']}")

    @staticmethod
    def log_request_up(parsed_data: dict) -> None:
        log.info(f"用例 env: {parsed_data['env']}")
        log.info(f"用例 module: {parsed_data['module']}")
        log.info(f"用例 name: {parsed_data['name']}")
        log.info(f"用例 description: {parsed_data['description']}")
        log.info(f"请求 method: {parsed_data['method']}")
        log.info(f"请求 url: {parsed_data['url']}")
        log.info(f"请求 params: {parsed_data['params']}")
        log.info(f"请求 headers: {parsed_data['headers']}")
        log.info(f"请求 data_type：{parsed_data['body_type']}")
        if parsed_data['body_type'] != BodyType.JSON:
            log.info(f"请求 data：{parsed_data['body']}")
        else:
            log.info(f"请求 json: {parsed_data['body']}")
        log.info(f"请求 files: {parsed_data['files_no_parse']}")

    @staticmethod
    def log_request_teardown(parsed_data: dict) -> None:
        log.info(f"请求 teardown_sql: {parsed_data['teardown_sql']}")
        log.info(f"请求 teardown_hooks: {parsed_data['teardown_hooks']}")
        log.info(f"请求 teardown_extract: {parsed_data['teardown_extract']}")
        log.info(f"请求 teardown_assert: {parsed_data['teardown_assert']}")
        log.info(f"请求 teardown_wait_time: {parsed_data['teardown_wait_time']}")

    @staticmethod
    def log_request_down(response_data: dict) -> None:
        log.info(f"请求发送时间: {response_data['stat']['execute_time']}")
        str_status_code = str(response_data['status_code'])
        if str_status_code.startswith('4') or str_status_code.startswith('5'):
            log.error(f"响应状态码: {response_data['status_code']}")
        else:
            log.success(f"响应状态码: {response_data['status_code']}")
        log.info(f"响应时间: {response_data['elapsed']} ms")

    @staticmethod
    def allure_request_setup(parsed_data: dict) -> None:
        allure_step(
            '请求前置',
            {
                'setup_testcase': parsed_data['setup_testcase'],
                'setup_sql': parsed_data['setup_sql'],
                'setup_hooks': parsed_data['setup_hooks'],
                'setup_wait_time': parsed_data['setup_wait_time'],
            },
        )

    @staticmethod
    def allure_request_up(parsed_data: dict) -> None:
        allure_step(
            '请求数据',
            {
                'env': parsed_data['env'],
                'module': parsed_data['module'],
                'name': parsed_data['name'],
                'case_id': parsed_data['case_id'],
                'description': parsed_data['description'],
                'method': parsed_data['method'],
                'url': parsed_data['url'],
                'params': parsed_data['params'],
                'headers': parsed_data['headers'],
                'data_type': parsed_data['body_type'],
                'data': parsed_data['body'],
                'files': parsed_data['files_no_parse'],
            },
        )

    @staticmethod
    def allure_request_teardown(parsed_data: dict) -> None:
        allure_step(
            '请求后置',
            {
                'teardown_sql': parsed_data['teardown_sql'],
                'teardown_hooks': parsed_data['teardown_hooks'],
                'teardown_extract': parsed_data['teardown_extract'],
                'teardown_assert': parsed_data['teardown_assert'],
                'teardown_wait_time': parsed_data['teardown_wait_time'],
            },
        )

    @staticmethod
    def allure_request_down(response_data: dict) -> None:
        allure_step(
            '响应数据',
            {
                'status_code': response_data['status_code'],
                'elapsed': response_data['elapsed'],
            },
        )

    @staticmethod
    def allure_dynamic_data(parsed_data: dict) -> None:
        allure.dynamic.title(parsed_data['name'])
        allure.dynamic.description(parsed_data['description'])
        allure.dynamic.link(parsed_data['url'])
        if parsed_data['allure_severity'] is not None:
            allure.dynamic.severity(parsed_data['allure_severity'])
        if parsed_data['files_no_parse'] is not None:
            for k, v in parsed_data['files_no_parse'].items():
                if isinstance(v, list):
                    for path in v:
                        allure_attach_file(path)
                else:
                    allure_attach_file(v)


send_request = SendRequests()
