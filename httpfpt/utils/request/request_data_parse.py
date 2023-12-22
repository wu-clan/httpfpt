#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from json import dumps as json_dumps
from string import Template
from typing import Union

import allure

from _pytest.outcomes import Skipped
from dirty_equals import IsUrl

from httpfpt.common.env_handler import get_env_dict
from httpfpt.common.errors import RequestDataParseError
from httpfpt.common.log import log
from httpfpt.core.path_conf import RUN_ENV_PATH
from httpfpt.enums.allure_severity_type import SeverityType
from httpfpt.enums.request.auth import AuthType
from httpfpt.enums.request.body import BodyType
from httpfpt.enums.request.engin import EnginType
from httpfpt.enums.request.method import MethodType
from httpfpt.utils.auth_plugins import AUTH_TYPE, IS_AUTH, AuthPlugins
from httpfpt.utils.enum_control import get_enum_values
from httpfpt.utils.request.hooks_executor import hooks_executor
from httpfpt.utils.request.vars_extractor import var_extractor

_RequestDataParamGetError = (KeyError, TypeError)


def _error_msg(info: str) -> str:
    msg_template = Template('测试用例数据解析失败, $info')
    return msg_template.substitute(info=info)


class RequestDataParse:
    def __init__(self, request_data: dict, request_engin: str):
        self.request_data = var_extractor.vars_replace(hooks_executor.hook_func_value_replace(request_data))
        self.request_engin = request_engin
        self._is_run()  # put bottom

    @property
    def config(self) -> dict:
        try:
            config = self.request_data['config']
        except _RequestDataParamGetError:
            raise RequestDataParseError(_error_msg('缺少 config 参数'))
        if not isinstance(config, dict):
            raise RequestDataParseError(_error_msg('参数 config 不是有效的 dict 类型'))
        else:
            return config

    @property
    def allure_epic(self) -> str:
        try:
            epic = self.request_data['config']['allure']['epic']
        except _RequestDataParamGetError:
            raise RequestDataParseError(_error_msg('缺少 config:allure:epic 参数'))
        else:
            if epic is None:
                raise RequestDataParseError(_error_msg('参数 config:allure:epic 为空'))
            if not isinstance(epic, str):
                raise RequestDataParseError(_error_msg('参数 config:allure:epic 不是有效的 str 类型'))
            return epic

    @property
    def allure_feature(self) -> str:
        try:
            feature = self.request_data['config']['allure']['feature']
        except _RequestDataParamGetError:
            raise RequestDataParseError(_error_msg('缺少 config:allure:feature 参数'))
        else:
            if feature is None:
                raise RequestDataParseError(_error_msg('参数 config:allure:feature 为空'))
            if not isinstance(feature, str):
                raise RequestDataParseError(_error_msg('参数 config:allure:feature 不是有效的 str 类型'))
            return feature

    @property
    def allure_story(self) -> str:
        try:
            story = self.request_data['config']['allure']['story']
        except _RequestDataParamGetError:
            raise RequestDataParseError(_error_msg('缺少 config:allure:story 参数'))
        else:
            if story is None:
                raise RequestDataParseError(_error_msg('参数 config:allure:story 为空'))
            if not isinstance(story, str):
                raise RequestDataParseError(_error_msg('参数 config:allure:story 不是有效的 str 类型'))
            return story

    @property
    def allure_severity(self) -> Union[str, None]:
        try:
            severity = self.request_data['config']['allure']['severity']
        except _RequestDataParamGetError:
            severity = None
        else:
            if severity is not None:
                if not isinstance(severity, str):
                    raise RequestDataParseError(_error_msg('参数 config:allure:severity 不是有效的 str 类型'))
                if severity not in get_enum_values(SeverityType):
                    raise RequestDataParseError(_error_msg('参数 config:allure:severity 输入不合法'))
        return severity

    @property
    def env(self) -> str:
        try:
            env = self.request_data['config']['request']['env']
        except _RequestDataParamGetError:
            raise RequestDataParseError(_error_msg('缺少 config:request:env 参数'))
        else:
            if env is None:
                raise RequestDataParseError(_error_msg('参数 config:request:env 为空'))
            if not isinstance(env, str):
                raise RequestDataParseError(_error_msg('参数 config:request:env 不是有效的 str 类型'))
            if not env.endswith('.env'):
                raise RequestDataParseError(_error_msg('参数 config:request:env 输入不合法'))
            return env

    @property
    def timeout(self) -> Union[int, None]:
        try:
            timeout = self.request_data['config']['request']['timeout']
            if timeout is not None:
                if not isinstance(timeout, int):
                    raise RequestDataParseError(_error_msg('参数 config:request:timeout 不是有效的 int 类型'))
        except _RequestDataParamGetError:
            timeout = None
        return timeout

    @property
    def verify(self) -> Union[bool, str, None]:
        try:
            verify = self.request_data['config']['request']['verify']
            if verify is not None:
                if not isinstance(verify, bool):
                    if not isinstance(verify, str):
                        raise RequestDataParseError(_error_msg('参数 config:request:verify 不是有效的 bool / str 类型'))
        except _RequestDataParamGetError:
            verify = None
        return verify

    @property
    def redirects(self) -> Union[bool, None]:
        try:
            redirects = self.request_data['config']['request']['redirects']
            if redirects is not None:
                if not isinstance(redirects, bool):
                    raise RequestDataParseError(_error_msg('参数 config:request:redirects 不是有效的 bool 类型'))
        except _RequestDataParamGetError:
            redirects = None
        return redirects

    @property
    def proxies(self) -> Union[dict, None]:
        try:
            proxies = self.request_data['config']['request']['proxies']
            if proxies is not None:
                if not isinstance(proxies, dict):
                    raise RequestDataParseError(_error_msg('参数 config:request:proxies 不是有效的 dict 类型'))
                keys = list(proxies.keys())
                if 'http' not in keys or 'https' not in keys:
                    raise RequestDataParseError(
                        _error_msg('测试用例数据解析失败，参数 config:request:proxies 不符合规范')
                    )
                for k, v in proxies.items():
                    if v is not None:
                        if not isinstance(v, str):
                            raise RequestDataParseError(
                                _error_msg(f'测试用例数据解析失败，参数 config:request:proxies:{v} 不是有效的 str 类型')
                            )
                if self.request_engin == EnginType.requests:
                    proxies = proxies
                elif self.request_engin == EnginType.httpx:
                    proxies = {'http://': proxies['http'], 'https://': proxies['https']}
        except _RequestDataParamGetError:
            proxies = None
        return proxies

    @property
    def module(self) -> str:
        try:
            module = self.request_data['config']['module']
        except _RequestDataParamGetError:
            raise RequestDataParseError(_error_msg('缺少 config:module 参数'))
        else:
            if module is None:
                raise RequestDataParseError(_error_msg('参数 config:module 为空'))
            if not isinstance(module, str):
                raise RequestDataParseError(_error_msg('参数 config:module 不是有效的 str 类型'))
            return module

    @property
    def test_steps(self) -> Union[dict, list]:
        try:
            test_steps = self.request_data['test_steps']
        except _RequestDataParamGetError:
            raise RequestDataParseError(_error_msg('请求参数解析失败，缺少 test_steps 参数'))
        else:
            if not isinstance(test_steps, (dict, list)):
                raise RequestDataParseError(_error_msg('参数 test_steps 不是有效的 dict / list 类型'))
            return test_steps

    @property
    def name(self) -> str:
        try:
            name = self.request_data['test_steps']['name']
        except _RequestDataParamGetError:
            raise RequestDataParseError(_error_msg('缺少 test_steps:name 参数'))
        else:
            if name is None:
                raise RequestDataParseError(_error_msg('参数 test_steps:name 为空'))
            if not isinstance(name, str):
                raise RequestDataParseError(_error_msg('参数 test_steps:name 不是有效的 str 类型'))
            return name

    @property
    def case_id(self) -> str:
        try:
            case_id = self.request_data['test_steps']['case_id']
        except _RequestDataParamGetError:
            raise RequestDataParseError(_error_msg('缺少 test_steps:case_id 参数'))
        else:
            if case_id is None:
                raise RequestDataParseError(_error_msg('参数 test_steps:case_id 为空'))
            if not isinstance(case_id, str):
                raise RequestDataParseError(_error_msg('参数 test_steps:case_id 不是有效的 str 类型'))
            return case_id

    @property
    def description(self) -> Union[str, None]:
        try:
            description = self.request_data['test_steps']['description']
            if not isinstance(description, str):
                raise RequestDataParseError(_error_msg('参数 test_steps:description 不是有效的 str 类型'))
        except _RequestDataParamGetError:
            description = None
        return description

    def _is_run(self) -> None:
        try:
            is_run = self.request_data['test_steps']['is_run']
        except _RequestDataParamGetError:
            pass
        else:
            if is_run is not None:
                if isinstance(is_run, bool):
                    if not is_run:
                        log.info(f'🏷️ ID: {self.case_id}')
                        allure.dynamic.title(self.name)
                        allure.dynamic.description(self.description)
                        log.warning('此用例已设置跳过执行')
                        raise Skipped('此用例已设置跳过执行')
                    return
                if isinstance(is_run, dict):
                    if 'reason' not in is_run.keys():
                        raise RequestDataParseError(_error_msg('参数 test_steps:is_run:skip 未设置 reason 参数'))
                    reason = is_run['reason'] or '未设置跳过原因'
                    if 'skip' in is_run.keys():
                        if isinstance(is_run['skip'], bool):
                            if is_run['skip']:
                                log.info(f'🏷️ ID: {self.case_id}')
                                allure.dynamic.title(self.name)
                                allure.dynamic.description(self.description)
                                log.warning(f'此用例已设置跳过执行: {reason}')
                                raise Skipped(f'此用例已设置跳过执行: {reason}')
                        else:
                            raise RequestDataParseError(_error_msg('参数 test_steps:is_run:skip 不是有效的 bool 类型'))
                    elif 'skip_if' in is_run.keys():
                        if isinstance(is_run['skip_if'], list):
                            for v in is_run['skip_if']:
                                if not isinstance(v, str):
                                    raise RequestDataParseError(
                                        _error_msg(f'参数 test_steps:is_run:skip_if:{v} 不是有效的 str 值')
                                    )
                                if hooks_executor.exec_any_code(v):
                                    log.info(f'🏷️ ID: {self.case_id}')
                                    allure.dynamic.title(self.name)
                                    allure.dynamic.description(self.description)
                                    log.warning(f'此用例已设置跳过执行: {reason}')
                                    raise Skipped(f'此用例已设置跳过执行: {reason}')
                    else:
                        raise RequestDataParseError(_error_msg('参数 test_steps:is_run 缺少 skip / skip_if 参数'))
                else:
                    raise RequestDataParseError(_error_msg('参数 test_steps:is_run 不是有效的 bool / dict 类型'))

    @property
    def method(self) -> str:
        try:
            method = self.request_data['test_steps']['request']['method']
        except _RequestDataParamGetError:
            raise RequestDataParseError(_error_msg('缺少 test_steps:request:method 参数'))
        else:
            if method is None:
                raise RequestDataParseError(_error_msg('参数 test_steps:request:method 为空'))
            if not isinstance(method, str):
                raise RequestDataParseError(_error_msg('参数 test_steps:request:method 不是有效的 str 类型'))
            if method.upper() not in get_enum_values(MethodType):
                raise RequestDataParseError(_error_msg('参数 test_steps:request:method 不是合法的请求类型'))
            return method.upper()

    @property
    def url(self) -> str:
        try:
            url = self.request_data['test_steps']['request']['url']
        except _RequestDataParamGetError:
            raise RequestDataParseError(_error_msg('缺少 test_steps:request:url 参数'))
        else:
            env = self.env
            try:
                env_file = os.path.join(RUN_ENV_PATH, env)
                env_dict = get_env_dict(env_file)
            except Exception as e:
                raise RequestDataParseError(f'环境变量 {env} 读取失败: {e}')
            host = env_dict.get('host') or env_dict.get('HOST')
            if host is None:
                raise RequestDataParseError(f'环境变量 {env_file} 读取失败, 缺少 HOST 参数')
            url = host + str(url)
            return url

    @property
    def params(self) -> Union[dict, bytes, None]:
        try:
            params = self.request_data['test_steps']['request']['params']
        except _RequestDataParamGetError:
            raise RequestDataParseError(_error_msg('缺少 test_steps:request:params 参数'))
        else:
            if params is not None:  # excel 数据处理
                if not isinstance(params, dict):
                    raise RequestDataParseError(_error_msg('参数 test_steps:request:params 不是有效的 dict 类型'))
        return params

    @property
    def headers(self) -> Union[dict, None]:
        try:
            headers = self.request_data['test_steps']['request']['headers']
        except _RequestDataParamGetError:
            raise RequestDataParseError(_error_msg('缺少 test_steps:request:headers 参数'))
        else:
            if headers is None:
                try:
                    headers = self.request_data['config']['request']['headers']
                except _RequestDataParamGetError:
                    headers = None
            else:
                if not isinstance(headers, dict):
                    raise RequestDataParseError(_error_msg('参数 test_steps:request:headers 不是有效的 dict 类型'))
            if headers is not None:
                if len(headers) == 0:
                    raise RequestDataParseError(_error_msg('参数 test_steps:request:headers 为空'))
            if IS_AUTH:
                if AUTH_TYPE == AuthType.bearer_token:
                    token = AuthPlugins().bearer_token
                    bearer_token = {'Authorization': f'Bearer {token}'}
                    headers = headers.update(bearer_token) if headers else bearer_token
            return headers

    @property
    def headers_auto_fix(self) -> dict:
        headers = self.headers
        body_type = self.body_type
        headers_format = headers or {}
        if body_type == BodyType.form_data:
            headers_format.update({'Content-Type': 'multipart/form-data'})
        elif body_type == BodyType.x_www_form_urlencoded:
            headers_format.update({'Content-Type': 'application/x-www-form-urlencoded'})
        elif body_type == BodyType.binary:
            headers_format.update({'Content-Type': 'application/octet-stream'})
        elif body_type == BodyType.GraphQL:
            headers_format.update({'Content-Type': 'application/json'})
        elif body_type == BodyType.TEXT:
            headers_format.update({'Content-Type': 'text/plain'})
        elif body_type == BodyType.JavaScript:
            headers_format.update({'Content-Type': 'application/javascript'})
        elif body_type == BodyType.JSON:
            headers_format.update({'Content-Type': 'application/json'})
        elif body_type == BodyType.HTML:
            headers_format.update({'Content-Type': 'text/html'})
        elif body_type == BodyType.XML:
            headers_format.update({'Content-Type': 'application/xml'})
        return headers_format

    @property
    def body_type(self) -> Union[str, None]:
        try:
            data_type = self.request_data['test_steps']['request']['body_type']
        except _RequestDataParamGetError:
            raise RequestDataParseError(_error_msg('缺少 test_steps:request:body_type 参数'))
        else:
            if data_type is not None:
                if data_type not in get_enum_values(BodyType):
                    raise RequestDataParseError(_error_msg('参数 test_steps:request:body_type 不是合法类型'))
        return data_type

    @property
    def body(self) -> Union[dict, bytes, str, None]:
        try:
            body = self.request_data['test_steps']['request']['body']
        except _RequestDataParamGetError:
            raise RequestDataParseError(_error_msg('缺少 test_steps:request:body 参数'))
        else:
            try:
                if body is not None:
                    body_type = self.body_type
                    if body_type is None:
                        raise RequestDataParseError('缺少 test_steps:request:body_type 参数')
                    elif body_type == BodyType.form_data:  # noqa: SIM114
                        body = body
                    elif body_type == BodyType.x_www_form_urlencoded:
                        body = body
                    elif body_type == BodyType.binary:
                        if isinstance(body, bytes):
                            body = bytes(body)
                        elif isinstance(body, str):
                            assert body == IsUrl(file_url=True)
                            if not os.path.exists(body):
                                raise RequestDataParseError(f'读取 test_steps:request:body:{body} 失败，文件不存在')
                            with open(body, 'rb') as f:
                                body = f.read()
                        else:
                            raise RequestDataParseError('参数 test_steps:request:body 不是有效的 str / bytes 类型')
                    elif body_type == BodyType.GraphQL:
                        if not isinstance(body, dict):
                            raise RequestDataParseError('参数 test_steps:request:body 不是有效的 dict 类型')
                        body = json_dumps(body, ensure_ascii=False).encode('utf-8')
                    elif body_type == BodyType.TEXT:  # noqa: SIM114
                        body = body
                    elif body_type == BodyType.JavaScript:
                        body = body
                    elif body_type == BodyType.JSON:
                        if not isinstance(body, dict):
                            raise RequestDataParseError('参数 test_steps:request:body 不是有效的 dict 类型')
                        body = json_dumps(body, ensure_ascii=False).encode('utf-8')
                    elif body_type == BodyType.HTML:  # noqa: SIM114
                        body = body
                    elif body_type == BodyType.XML:
                        body = body
            except Exception as e:
                raise RequestDataParseError(_error_msg(e.__str__()))
        return body

    @property
    def files(self) -> Union[dict, list, None]:
        files = self.files_no_parse
        if files is not None:
            for k, v in files.items():
                try:
                    # 多文件
                    if isinstance(v, list):
                        files = [(f'{k}', open(_, 'rb')) for _ in v]
                    # 单文件
                    else:
                        files = {f'{k}': open(v, 'rb')}
                except FileNotFoundError:
                    raise RequestDataParseError(_error_msg(f'参数 test_steps:request:files:{k} 文件不存在'))
        return files

    @property
    def files_no_parse(self) -> Union[dict, None]:
        try:
            files = self.request_data['test_steps']['request']['files']
        except _RequestDataParamGetError:
            raise RequestDataParseError(_error_msg('缺少 test_steps:request:files 参数'))
        else:
            if files is not None:
                if not isinstance(files, dict):
                    raise RequestDataParseError(_error_msg('参数 test_steps:request:files 不是有效的 dict 类型'))
        return files

    @property
    def is_setup(self) -> bool:
        try:
            setup = self.request_data['test_steps']['setup']
        except _RequestDataParamGetError:
            return False
        else:
            if setup is not None:
                return True
            else:
                return False

    @property
    def setup_testcase(self) -> Union[list, None]:
        try:
            testcase = self.request_data['test_steps']['setup']['testcase']
            if testcase is not None:
                if not isinstance(testcase, list):
                    raise RequestDataParseError(_error_msg('参数 test_steps:setup:testcase 不是有效的 list 类型'))
                else:
                    for i in testcase:
                        if isinstance(i, dict):
                            for k, v in i.items():
                                if not isinstance(v, str):
                                    raise RequestDataParseError(
                                        _error_msg(f'参数 test_steps:setup:testcase:{k} 不是有效的 str 类型')
                                    )
                        else:
                            if not isinstance(i, str):
                                raise RequestDataParseError(
                                    _error_msg(f'参数 test_steps:setup:testcase:{i} 不是有效的 str 类型')
                                )
        except _RequestDataParamGetError:
            testcase = None
        return testcase

    @property
    def setup_sql(self) -> Union[list, None]:
        try:
            sql = self.request_data['test_steps']['setup']['sql']
            if sql is not None:
                if not isinstance(sql, list):
                    raise RequestDataParseError(_error_msg('参数 test_steps:setup:sql 不是有效的 list 类型'))
                else:
                    for i in sql:
                        if isinstance(i, dict):
                            for k, v in i.items():
                                if k != 'value':
                                    if not isinstance(v, str):
                                        raise RequestDataParseError(
                                            _error_msg(f'参数 test_steps:setup:sql:{k} 不是有效的 str 类型')
                                        )
                        else:
                            if not isinstance(i, str):
                                raise RequestDataParseError(
                                    _error_msg(f'参数 test_steps:setup:sql:{i} 不是有效的 str 类型'),
                                )
        except _RequestDataParamGetError:
            sql = None
        return sql

    @property
    def setup_hooks(self) -> Union[list, None]:
        try:
            hook = self.request_data['test_steps']['setup']['hooks']
            if hook is not None:
                if not isinstance(hook, list):
                    raise RequestDataParseError(_error_msg('参数 test_steps:setup:hook 不是有效的 list 类型'))
                else:
                    for v in hook:
                        if not isinstance(v, str):
                            raise RequestDataParseError(
                                _error_msg(f'参数 test_steps:setup:hooks:{v} 不是有效的 str 类型'),
                            )
        except _RequestDataParamGetError:
            hook = None
        return hook

    @property
    def setup_wait_time(self) -> Union[int, None]:
        try:
            time = self.request_data['test_steps']['setup']['wait_time']
            if time is not None:
                if not isinstance(time, int):
                    raise RequestDataParseError(_error_msg('参数 test_steps:setup:wait_time 不是有效的 int 类型'))
        except _RequestDataParamGetError:
            time = None
        return time

    @property
    def is_teardown(self) -> bool:
        try:
            teardown = self.request_data['test_steps']['teardown']
        except _RequestDataParamGetError:
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
                if not isinstance(sql, list):
                    raise RequestDataParseError(_error_msg('参数 test_steps:teardown:sql 不是有效的 list 类型'))
                else:
                    for i in sql:
                        if isinstance(i, dict):
                            for k, v in i.items():
                                if k != 'value':
                                    if not isinstance(v, str):
                                        raise RequestDataParseError(
                                            _error_msg(f'参数 test_steps:teardown:sql:{k} 不是有效的 str 类型'),
                                        )
                        else:
                            if not isinstance(i, str):
                                raise RequestDataParseError(
                                    _error_msg(f'参数 test_steps:teardown:sql:{i} 不是有效的 str 类型'),
                                )
        except _RequestDataParamGetError:
            sql = None
        return sql

    @property
    def teardown_hooks(self) -> Union[list, None]:
        try:
            hook = self.request_data['test_steps']['teardown']['hooks']
            if hook is not None:
                if not isinstance(hook, list):
                    raise RequestDataParseError(_error_msg('参数 test_steps:teardown:hook 不是有效的 list 类型'))
                else:
                    for v in hook:
                        if not isinstance(v, str):
                            raise RequestDataParseError(
                                _error_msg(f'参数 test_steps:teardown:hooks:{v} 不是有效的 str 类型'),
                            )
        except _RequestDataParamGetError:
            hook = None
        return hook

    @property
    def teardown_extract(self) -> Union[list, None]:
        try:
            extract = self.request_data['test_steps']['teardown']['extract']
            if extract is not None:
                if not isinstance(extract, list):
                    raise RequestDataParseError(_error_msg('参数 test_steps:teardown:extract 不是有效的 list 类型'))
                else:
                    for i in extract:
                        if isinstance(i, dict):
                            for k, v in i.items():
                                if not isinstance(v, str):
                                    raise RequestDataParseError(
                                        _error_msg(f'参数 test_steps:teardown:extract:{k} 不是有效的 str 类型')
                                    )
                        else:
                            raise RequestDataParseError(_error_msg('参数 test_steps:teardown:extract:{i} 不是合法数据'))
        except _RequestDataParamGetError:
            extract = None
        return extract

    @property
    def teardown_assert(self) -> Union[str, list, dict, None]:
        try:
            assert_text = self.request_data['test_steps']['teardown']['assert']
        except _RequestDataParamGetError:
            assert_text = None
        if assert_text is not None:
            if not any([isinstance(assert_text, str), isinstance(assert_text, list)]):
                raise RequestDataParseError(_error_msg('参数 test_steps:teardown:assert 不是有效的 str / list 类型'))
        return assert_text

    @property
    def teardown_wait_time(self) -> Union[int, None]:
        try:
            time = self.request_data['test_steps']['teardown']['wait_time']
            if time is not None:
                if not isinstance(time, int):
                    raise RequestDataParseError(_error_msg('参数 test_steps:teardown:wait_time 不是有效的 int 类型'))
        except _RequestDataParamGetError:
            time = None
        return time

    @property
    def get_request_data_parsed(self) -> dict:
        """
        获取所有解析后的请求数据

        :return:
        """
        all_data = {
            'config': self.config,
            'allure_epic': self.allure_epic,
            'allure_feature': self.allure_feature,
            'allure_story': self.allure_story,
            'allure_severity': self.allure_severity,
            'env': self.env,
            'timeout': self.timeout,
            'verify': self.verify,
            'redirects': self.redirects,
            'proxies': self.proxies,
            'module': self.module,
            'test_steps': self.test_steps,
            'name': self.name,
            'case_id': self.case_id,
            'description': self.description,
            'method': self.method,
            'url': self.url,
            'params': self.params,
            'headers': self.headers_auto_fix,
            'body_type': self.body_type,
            'body': self.body,
            'files': self.files,
            'files_no_parse': self.files_no_parse,
            'is_setup': self.is_setup,
            'setup_testcase': self.setup_testcase,
            'setup_sql': self.setup_sql,
            'setup_hooks': self.setup_hooks,
            'setup_wait_time': self.setup_wait_time,
            'is_teardown': self.is_teardown,
            'teardown_sql': self.teardown_sql,
            'teardown_hooks': self.teardown_hooks,
            'teardown_extract': self.teardown_extract,
            'teardown_assert': self.teardown_assert,
            'teardown_wait_time': self.teardown_wait_time,
        }
        return all_data
