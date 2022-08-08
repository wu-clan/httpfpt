#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
from typing import Union, Any

import allure
from _pytest.outcomes import Skipped

from fastpt.common.env_handler import get_env_dict
from fastpt.common.log import log
from fastpt.core.path_conf import RUN_ENV_PATH
from fastpt.utils.request.vars_extract import VarsExtractor


class RequestDataParse:

    def __init__(self, request_data: dict):
        self.request_data = VarsExtractor().vars_replace(request_data)
        self._is_run()  # put down

    @property
    def allure_epic(self) -> str:
        try:
            epic = self.request_data['config']['allure']['epic']
        except KeyError:
            raise KeyError('测试用例数据解析失败, 缺少 config:allure:epic 参数')
        else:
            if epic is None:
                raise ValueError('测试用例数据解析失败, 参数 config:allure:epic 为空')
            return epic

    @property
    def allure_feature(self) -> str:
        try:
            feature = self.request_data['config']['allure']['feature']
        except KeyError:
            raise ValueError('测试用例数据解析失败, 缺少 config:allure:feature 参数')
        else:
            if feature is None:
                raise ValueError('测试用例数据解析失败, 参数 config:allure:feature 为空')
            return feature

    @property
    def allure_story(self) -> str:
        try:
            story = self.request_data['config']['allure']['story']
        except KeyError:
            raise ValueError('测试用例数据解析失败, 缺少 config:allure:story 参数')
        else:
            if story is None:
                raise ValueError('测试用例数据解析失败, 参数 config:allure:story 为空')
            return story

    @property
    def env(self) -> str:
        try:
            env = self.request_data['config']['request']['env']
        except KeyError:
            raise ValueError('测试用例数据解析失败, 缺少 config:request:env 参数')
        else:
            if env is None:
                raise ValueError('测试用例数据解析失败, 参数 config:request:env 为空')
            if not isinstance(env, str):
                raise ValueError('测试用例数据解析失败, 参数 config:request:env 不是有效的 str 类型')
            if not env.endswith('.env'):
                raise ValueError('测试用例数据解析失败, 参数 config:request:env 输入不合法')
            return env

    @property
    def timeout(self) -> Union[int, None]:
        try:
            timeout = self.request_data['config']['request']['timeout']
            if not isinstance(timeout, int):
                raise ValueError('测试用例数据解析失败, 参数 config:request:timeout 不是有效的 int 类型')
        except KeyError:
            timeout = None
        return timeout

    @property
    def verify(self) -> Union[bool, str, None]:
        try:
            verify = self.request_data['config']['request']['verify']
            if not isinstance(verify, bool):
                if not isinstance(verify, str):
                    raise ValueError('测试用例数据解析失败, 参数 config:request:verify 不是有效的 bool / str 类型')
        except KeyError:
            verify = None
        return verify

    @property
    def redirects(self) -> Union[bool, None]:
        try:
            redirects = self.request_data['config']['request']['redirects']
            if not isinstance(redirects, bool):
                raise ValueError('测试用例数据解析失败, 参数 config:request:redirects 不是有效的 bool 类型')
        except KeyError:
            redirects = None
        return redirects

    @property
    def proxies(self) -> Union[dict, None]:
        try:
            proxies = self.request_data['config']['request']['proxies']
            for k, v in proxies.items():
                if k == 'requests' or k == 'httpx':
                    proxies = v
                    if not isinstance(proxies, dict):
                        raise ValueError('测试用例数据解析失败, 参数 config:request:proxies 不是有效的 dict 类型')
                else:
                    raise ValueError('测试用例数据解析失败, 参数 config:request:proxies 不符合规范')
        except KeyError:
            proxies = None
        return proxies

    @property
    def module(self) -> str:
        try:
            module = self.request_data['config']['module']
        except KeyError:
            raise ValueError('测试用例数据解析失败, 缺少 config:module 参数')
        else:
            if module is None:
                raise ValueError('测试用例数据解析失败, 参数 config:module 为空')
            return module

    @property
    def name(self) -> str:
        try:
            name = self.request_data['test_steps']['name']
        except KeyError:
            raise ValueError('测试用例数据解析失败, 缺少 test_steps:name 参数')
        else:
            if name is None:
                raise ValueError('测试用例数据解析失败, 参数 test_steps:name 为空')
            return name

    @property
    def case_id(self) -> str:
        try:
            case_id = self.request_data['test_steps']['case_id']
        except KeyError:
            raise ValueError('测试用例数据解析失败, 缺少 test_steps:case_id 参数')
        else:
            if case_id is None:
                raise ValueError('测试用例数据解析失败, 参数 test_steps:case_id 为空')
            return case_id

    @property
    def description(self) -> Union[str, None]:
        try:
            description = self.request_data['test_steps']['description']
            if not isinstance(description, str):
                raise ValueError('测试用例数据解析失败, 参数 test_steps:description 不是有效的 str 类型')
        except KeyError:
            description = None
        return description

    def _is_run(self):
        try:
            is_run = self.request_data['test_steps']['is_run']
        except KeyError:
            ...
        else:
            if is_run is not None:
                if not is_run or str(is_run).lower() == 'false':
                    allure.dynamic.title(
                        f"用例 module: {self.module};"
                        f"用例 case_id: {self.case_id}"
                    )
                    log.warning('此用例已设置跳过')
                    raise Skipped('此用例已设置跳过')

    @property
    def method(self) -> str:
        try:
            method = self.request_data['test_steps']['request']['method']
        except KeyError:
            raise ValueError('请求参数解析失败, 缺少 test_steps:request:method 参数')
        else:
            if method is None:
                raise ValueError('请求参数解析失败, 参数 test_steps:request:method 为空')
            if not isinstance(method, str):
                raise ValueError('请求参数解析失败, 参数 test_steps:request:method 不是有效的 str 类型')
            if not any(_ == method.lower() for _ in ['get', 'post', 'put', 'delete', 'patch']):
                raise ValueError('请求参数解析失败, 参数 test_steps:request:method 不是合法的请求类型')
            return method

    @property
    def url(self) -> str:
        try:
            url = self.request_data['test_steps']['request']['url']
        except KeyError:
            raise ValueError('请求参数解析失败, 缺少 test_steps:request:url 参数')
        else:
            env_file = os.path.join(RUN_ENV_PATH, self.env)
            host = get_env_dict(env_file)['host']
            url = host + str(url)
            return url

    @property
    def params(self) -> Union[dict, bytes, None]:
        try:
            params = self.request_data['test_steps']['request']['params']
        except KeyError:
            raise ValueError('请求数据解析失败, 缺少 test_steps:request:params 参数')
        else:
            if params is not None:
                if isinstance(params, str):
                    params = eval(params)
        return params

    @property
    def headers(self) -> Union[dict, None]:
        try:
            headers = self.request_data['test_steps']['request']['headers']
        except KeyError:
            raise ValueError('请求数据解析失败, 缺少 test_steps:request:headers 参数')
        else:
            if headers is None:
                try:
                    headers = self.request_data['config']['request']['headers']
                except KeyError:
                    headers = None
            if headers is not None:
                if isinstance(headers, str):
                    headers = eval(headers)
                if not isinstance(headers, dict):
                    raise ValueError('请求数据解析失败, 参数 headers 格式错误, 必须为 dict 类型')
            return headers

    @property
    def data_type(self) -> Union[str, None]:
        try:
            data_type = self.request_data['test_steps']['request']['data_type']
        except KeyError:
            raise ValueError('请求数据解析失败, 缺少 test_steps:request:data_type 参数')
        else:
            if not any(_ == data_type for _ in ['data', 'json', None]):
                raise ValueError('请求参数解析失败, 参数 test_steps:request:data_type 不是合法类型')
            if data_type is not None:
                data_type = data_type.lower()
        return data_type

    @property
    def data(self) -> Union[dict, None]:
        try:
            data = self.request_data['test_steps']['request']['data']
        except KeyError:
            raise ValueError('请求数据解析失败, 缺少 test_steps:request:data 参数')
        else:
            if data is not None:
                if isinstance(data, str):
                    data = eval(data)
                if self.data_type == 'json':
                    try:
                        data = json.dumps(data, ensure_ascii=False)
                    except Exception:
                        raise ValueError('请求数据解析失败, 请求参数 data 不是有效的 dict')
        return data

    @property
    def files(self) -> Union[dict, list, None]:
        try:
            files = self.request_data['test_steps']['request']['files']
        except KeyError:
            raise ValueError('请求数据解析失败, 缺少 test_steps:request:files 参数')
        else:
            if files is not None:
                if isinstance(files, str):
                    files = eval(files)
                if not isinstance(files, dict):
                    raise ValueError('请求数据解析失败, 参数 test_steps:request:files 不是有效的 dict 类型')
                for k, v in files.items():
                    # 多文件
                    if isinstance(v, list):
                        files = [(f'{k}', open(_, 'rb')) for _ in v]
                    # 单文件
                    else:
                        files = {f'{k}': open(v, "rb")}
        return files

    @property
    def files_no_parse(self) -> Union[dict, None]:
        try:
            files = self.request_data['test_steps']['request']['files']
        except KeyError:
            raise ValueError('请求数据解析失败, 缺少 test_steps:request:files 参数')
        else:
            if files is not None:
                if isinstance(files, str):
                    files = eval(files)
                if not isinstance(files, dict):
                    raise ValueError('请求数据解析失败, 参数 test_steps:request:files 不是有效的 dict 类型')
        return files

    @property
    def is_setup(self) -> bool:
        try:
            setup = self.request_data['test_steps']['setup']
        except KeyError:
            return False
        else:
            if setup is not None:
                return True
            else:
                return False

    @property
    def setup_sql(self) -> Union[list, None]:
        try:
            sql = self.request_data['test_steps']['setup']['sql']
            if sql is not None:
                if isinstance(sql, str):
                    sql = eval(sql)
                if not isinstance(sql, list):
                    raise ValueError('请求数据解析失败, 参数 test_steps:setup:sql 不是有效的 list 类型')
        except KeyError:
            sql = None
        return sql

    @property
    def setup_hooks(self):
        try:
            hook = self.request_data['test_steps']['setup']['hooks']
            if hook is not None:
                if isinstance(hook, str):
                    hook = eval(hook)
                if not isinstance(hook, list):
                    raise ValueError('请求数据解析失败, 参数 test_steps:setup:hook 不是有效的 list 类型')
        except KeyError:
            hook = None
        return hook

    @property
    def setup_wait_time(self):
        try:
            time = self.request_data['test_steps']['setup']['wait_time']
            if time is not None:
                if isinstance(time, str):
                    time = eval(time)
                if not isinstance(time, int):
                    raise ValueError('请求数据解析失败, 参数 test_steps:setup:wait_time 不是有效的 int 类型')
        except KeyError:
            time = None
        return time

    @property
    def is_teardown(self) -> bool:
        try:
            teardown = self.request_data['test_steps']['setup']
        except KeyError:
            return False
        else:
            if teardown is not None:
                return True
            else:
                return False

    @property
    def teardown_sql(self) -> Union[list, None]:
        try:
            sql = self.request_data['test_steps']['teardown']['sql']
            if sql is not None:
                if isinstance(sql, str):
                    sql = eval(sql)
                if not isinstance(sql, list):
                    raise ValueError('请求数据解析失败, 参数 test_steps:teardown:sql 不是有效的 list 类型')
        except KeyError:
            sql = None
        return sql

    @property
    def teardown_hooks(self) -> Any:
        try:
            hook = self.request_data['test_steps']['teardown']['hooks']
            if hook is not None:
                if isinstance(hook, str):
                    hook = eval(hook)
                if not isinstance(hook, list):
                    raise ValueError('请求数据解析失败, 参数 test_steps:teardown:hook 不是有效的 list 类型')
        except KeyError:
            hook = None
        return hook

    @property
    def teardown_extract(self):
        try:
            extract = self.request_data['test_steps']['teardown']['extract']
            if extract is not None:
                if isinstance(extract, str):
                    extract = eval(extract)
                if not isinstance(extract, list):
                    raise ValueError('请求数据解析失败, 参数 test_steps:teardown:extract 不是有效的 list 类型')
        except KeyError:
            extract = None
        return extract

    @property
    def teardown_assert(self) -> Union[str, list, dict, None]:
        try:
            assert_text = self.request_data['test_steps']['teardown']['assert']
        except KeyError:
            assert_text = None
        if assert_text is not None:
            if isinstance(assert_text, str):
                # 单条 code 断言时, 跳过处理
                if not assert_text.startswith('assert'):
                    assert_text = eval(assert_text)
            if not any([isinstance(assert_text, list), isinstance(assert_text, dict)]):
                raise ValueError(
                    '请求参数解析失败, 参数 test_steps:teardown:assert 不是有效的 str / dict / list 类型'
                )
        return assert_text

    @property
    def teardown_wait_time(self):
        try:
            time = self.request_data['test_steps']['teardown']['wait_time']
            if time is not None:
                if isinstance(time, str):
                    time = eval(time)
                if not isinstance(time, int):
                    raise ValueError('请求数据解析失败, 参数 test_steps:teardown:wait_time 不是有效的 int 类型')
        except KeyError:
            time = None
        return time

    @property
    def get_request_args_parsed(self) -> dict:
        """
        获取解析后的请求参数

        :return:
        """
        if self.data_type != 'json':
            parsed_data = {
                'method': self.method,
                'url': self.url,
                'params': self.params,
                'headers': self.headers,
                'data': self.data,
                'files': self.files
            }
        else:
            parsed_data = {
                'method': self.method,
                'url': self.url,
                'params': self.params,
                'headers': self.headers,
                'json': self.data,
                'files': self.files
            }
        return parsed_data
