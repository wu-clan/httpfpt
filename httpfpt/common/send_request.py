#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import time

from json import JSONDecodeError

import allure
import httpx
import requests
import stamina

from _pytest.outcomes import Skipped
from httpx import Response as HttpxResponse
from requests import Response as RequestsResponse

from httpfpt.common.errors import AssertError, SendRequestError
from httpfpt.common.log import log
from httpfpt.core.get_conf import config
from httpfpt.db.mysql_db import mysql_client
from httpfpt.enums.request.body import BodyType
from httpfpt.enums.request.engin import EnginType
from httpfpt.enums.setup_type import SetupType
from httpfpt.enums.teardown_type import TeardownType
from httpfpt.utils.allure_control import allure_attach_file, allure_step
from httpfpt.utils.assert_control import asserter
from httpfpt.utils.enum_control import get_enum_values
from httpfpt.utils.relate_testcase_executor import exec_setup_testcase
from httpfpt.utils.request.hook_executor import hook_executor
from httpfpt.utils.request.request_data_parse import RequestDataParse
from httpfpt.utils.request.vars_extractor import var_extractor
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
        kwargs['timeout'] = kwargs['timeout'] or config.REQUEST_TIMEOUT
        kwargs['verify'] = kwargs['verify'] or config.REQUEST_VERIFY
        kwargs['proxies'] = kwargs['proxies'] or config.REQUEST_PROXIES_REQUESTS
        kwargs['allow_redirects'] = kwargs['allow_redirects'] or config.REQUEST_REDIRECTS
        request_retry = kwargs['retry'] or config.REQUEST_RETRY
        del kwargs['retry']
        # 消除安全警告
        requests.packages.urllib3.disable_warnings()  # type: ignore
        log.info('开始发送请求...')
        try:
            for attempt in stamina.retry_context(on=requests.HTTPError, attempts=request_retry):
                with attempt:
                    if stamina.is_active():
                        log.warning('请求响应异常重试...')
                    response = requests.session().request(**kwargs)
                    response.raise_for_status()
        except Exception as e:
            log.error(f'发送 requests 请求响应异常: {e}')
            raise SendRequestError(e.__str__())
        else:
            return response  # type: ignore

    @staticmethod
    def _httpx_engin(**kwargs) -> HttpxResponse:
        """
        httpx 引擎

        :param kwargs:
        :return:
        """
        kwargs['timeout'] = kwargs['timeout'] or config.REQUEST_TIMEOUT
        verify = kwargs['verify'] or config.REQUEST_VERIFY
        proxies = kwargs['proxies'] or config.REQUEST_PROXIES_HTTPX
        redirects = kwargs['allow_redirects'] or config.REQUEST_REDIRECTS
        request_retry = kwargs['retry'] or config.REQUEST_RETRY
        del kwargs['verify']
        del kwargs['proxies']
        del kwargs['allow_redirects']
        del kwargs['retry']
        log.info('开始发送请求...')
        try:
            with httpx.Client(verify=verify, proxies=proxies, follow_redirects=redirects) as client:  # type: ignore
                for attempt in stamina.retry_context(on=httpx.HTTPError, attempts=request_retry):
                    with attempt:
                        if stamina.is_active():
                            log.warning('请求响应异常重试...')
                        response = client.request(**kwargs)
                        response.raise_for_status()
        except Exception as e:
            log.error(f'发送 httpx 请求响应异常: {e}')
            raise SendRequestError(e.__str__())
        else:
            return response  # type: ignore

    def send_request(
        self,
        request_data: dict,
        *,
        request_engin: EnginType = EnginType.requests,
        log_data: bool = True,
        relate_log: bool = False,
        **kwargs,
    ) -> dict:
        """
        发送请求

        :param request_data: 请求数据
        :param request_engin: 请求引擎
        :param log_data: 日志记录数据
        :param relate_log: 关联测试用例
        :return: response
        """
        if request_engin not in get_enum_values(EnginType):
            raise SendRequestError('请求发起失败，请使用合法的请求引擎')

        # 获取解析后的请求数据
        log.info('开始解析请求数据...' if not relate_log else '开始解析关联请求数据...')
        try:
            request_data_parse = RequestDataParse(request_data, request_engin)
            parsed_data = request_data_parse.get_request_data_parsed()
            if not relate_log:
                log.info(f'🏷️ ID: {parsed_data["case_id"]}')
        except Skipped as e:
            raise e
        except Exception as e:
            if not relate_log:
                log.error(f'请求数据解析失败: {e}')
            raise e
        log.info('请求数据解析完成' if not relate_log else '关联请求数据解析完成')

        # 记录请求前置数据; 此处数据中如果包含关联用例变量, 不会被替换为结果记录, 因为替换动作还未发生
        setup = parsed_data['setup']
        if log_data:
            if setup:
                self.log_request_setup(setup)

        # 前置处理
        if parsed_data['is_setup']:
            log.info('开始处理请求前置...')
            try:
                for item in setup:
                    for key, value in item.items():
                        if value is not None:
                            if key == SetupType.TESTCASE:
                                relate_parsed_data = exec_setup_testcase(parsed_data, value)
                                if relate_parsed_data:
                                    parsed_data = relate_parsed_data
                            elif key == SetupType.SQL:
                                mysql_client.exec_case_sql(value, parsed_data['env'])
                            elif key == SetupType.HOOK:
                                hook_executor.exec_hook_func(value)
                            elif key == SetupType.WAIT_TIME:
                                time.sleep(value)
                                log.info(f'执行请求前等待：{value} s')
            except Exception as e:
                log.error(f'请求前置处理异常: {e}')
                raise e
            log.info('请求前置处理完成')

        # 日志记录请求数据
        if log_data:
            self.log_request_up(parsed_data)
            self.allure_request_up(parsed_data)

        # allure 记录动态数据
        self.allure_dynamic_data(parsed_data)

        # 整理请求参数
        request_conf = {
            'timeout': parsed_data['timeout'],
            'verify': parsed_data['verify'],
            'proxies': parsed_data['proxies'],
            'allow_redirects': parsed_data['redirects'],
        }
        request_data_parsed = {
            'method': parsed_data['method'],
            'url': parsed_data['url'],
            'params': parsed_data['params'],
            'headers': parsed_data['headers'],
            'data': parsed_data['body'],
            'files': parsed_data['files'],
            'retry': parsed_data['retry'],
        }
        if parsed_data['body_type'] == BodyType.JSON or parsed_data['body_type'] == BodyType.GraphQL:
            request_data_parsed.update({'json': request_data_parsed.pop('data')})
        elif parsed_data['body_type'] == BodyType.binary:
            if request_engin == EnginType.httpx:
                request_data_parsed.update({'content': request_data_parsed.pop('data')})

        # 发送请求
        response_data = self.init_response_metadata
        response_data['stat']['execute_time'] = get_current_time()
        if request_engin == EnginType.requests:
            response = self._requests_engin(**request_conf, **request_data_parsed, **kwargs)
        elif request_engin == EnginType.httpx:
            response = self._httpx_engin(**request_conf, **request_data_parsed, **kwargs)
        else:
            raise SendRequestError('请求发起失败，请使用合法的请求引擎：requests / httpx')

        # 记录响应数据
        response_data['url'] = str(response.url)
        response_data['status_code'] = int(response.status_code)
        response_data['elapsed'] = response.elapsed.microseconds / 1000.0
        response_data['headers'] = dict(response.headers)
        response_data['cookies'] = dict(response.cookies)
        try:
            json_data = response.json()
        except JSONDecodeError:
            log.warning('响应数据解析失败，响应数据不是有效的 json 格式')
            json_data = {}
        response_data['json'] = json_data
        response_data['content'] = response.content.decode('utf-8')
        response_data['text'] = response.text

        # 日志记录响应数据
        teardown = parsed_data['teardown']
        if log_data:
            self.log_request_down(response_data)
            self.allure_request_down(response_data)
            if teardown:
                self.log_request_teardown(teardown)

        # 后置处理
        if parsed_data['is_teardown']:
            log.info('开始处理请求后置...')
            try:
                for item in teardown:
                    for key, value in item.items():
                        if value is not None:
                            if key == TeardownType.SQL:
                                mysql_client.exec_case_sql(value, parsed_data['env'])
                            if key == TeardownType.HOOK:
                                hook_executor.exec_hook_func(value)
                            if key == TeardownType.EXTRACT:
                                var_extractor.teardown_var_extract(response_data, value, parsed_data['env'])
                            if key == TeardownType.ASSERT:
                                asserter.exec_asserter(response_data, assert_text=value)
                            elif key == TeardownType.WAIT_TIME:
                                log.info(f'执行请求后等待：{value} s')
                                time.sleep(value)
            except AssertionError as e:
                log.error(f'断言失败: {e}')
                raise AssertError(f'断言失败: {e}')
            except Exception as e:
                log.error(f'请求后置处理异常: {e}')
                raise e
            log.info('请求后置处理完成')

        return response_data

    def log_request_setup(self, setup: list) -> None:
        for item in setup:
            for key, value in item.items():
                if key == SetupType.TESTCASE:
                    log.info(f'前置 setup_testcase: {value}')
                    self.allure_request_setup({'setup_testcase': value})
                elif key == SetupType.SQL:
                    log.info(f'前置 setup_sql: {value}')
                    self.allure_request_setup({'setup_sql': value})
                elif key == SetupType.HOOK:
                    log.info(f'前置 setup_hook: {value}')
                    self.allure_request_setup({'setup_hook': value})
                elif key == SetupType.WAIT_TIME:
                    log.info(f'前置 setup_wait_time: {value}')
                    self.allure_request_setup({'setup_wait_time': value})

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
        log.info(f"请求 retry: {parsed_data['retry']}")

    def log_request_teardown(self, teardown: list) -> None:
        for item in teardown:
            for key, value in item.items():
                if key == TeardownType.SQL:
                    log.info(f'后置 teardown_sql: {value}')
                    self.allure_request_teardown({'teardown_sql': value})
                elif key == TeardownType.HOOK:
                    log.info(f'后置 teardown_hook: {value}')
                    self.allure_request_teardown({'teardown_hook': value})
                elif key == TeardownType.EXTRACT:
                    log.info(f'后置 teardown_extract: {value}')
                    self.allure_request_teardown({'teardown_extract': value})
                elif key == TeardownType.ASSERT:
                    log.info(f'后置 teardown_assert: {value}')
                    self.allure_request_teardown({'teardown_assert': value})
                elif key == TeardownType.WAIT_TIME:
                    log.info(f'后置 teardown_wait_time: {value}')
                    self.allure_request_teardown({'teardown_wait_time': value})

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
    def allure_request_setup(setup_log: dict) -> None:
        allure_step('请求前置', setup_log)

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
    def allure_request_teardown(teardown_log: dict) -> None:
        allure_step('请求后置', teardown_log)

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
