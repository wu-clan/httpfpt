#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import re

from decimal import Decimal
from typing import Any

from jsonpath import findall
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from httpfpt.common.errors import AssertSyntaxError, JsonPathFindError
from httpfpt.common.log import log
from httpfpt.db.mysql import mysql_client
from httpfpt.enums.assert_type import AssertType
from httpfpt.enums.sql_type import SqlType


class Asserter:
    def _code_asserter(self, response: dict, assert_text: str) -> None:
        """
        **代码断言器, 像 pytest 断言一样使用它**

        基本语法::
            1. assert  期望值 条件 取值表达式(pm.response.get()...)
            2. assert 期望值 条件 取值表达式(pm.response.get()...), 错误信息(可选, 如果不填写, 记得去掉前面的逗号, 建议填写)

        扩展语法::
            dirty-equals 断言库专属, 请不要在断言内容中使用带有函数引用的断言方式, 仅支持简易验证操作, 使用前,
            请阅读它的使用文档, `github <https://github.com/samuelcolvin/dirty-equals>`_

            1. assert 取值表达式(pm.response.get()...) 条件(== 或 !=) 类型

        取值说明::
            与 postman 相似, 但又完全不同, 你只能通过全程手动脚本来控制断言数据, 并且, 需要以 pm.response.get 作为比较值的开头,
            后面获取的内容中, 需要以 .get() 为基础, 视情况添加 python 代码的一些简单方法并确保它们符合常规 assert 语法

        取值范围::

            {
                'url': '',
                'status_code': 200,
                'elapsed': 0,
                'headers': {},
                'cookies': {},
                'result': {},
                'content': {},
                'text': {},
                'stat': {'execute_time': 'None'},
                'sql_data': {},
            }

        一些简单的例子::
            1. assert 200 == pm.response.get('status_code')
            2. assert 'success' != pm.response.get('msg')[1]
            3. assert 'com' in pm.response.get('content').get('url')
            4. assert pm.response.get('header').get('httpfpt') == IsDict(version=0.0.1)
            5. assert pm.response.get('content').get('id') == IsUUID

        :param response:
        :param assert_text:
        :return:
        """  # noqa: E501
        log.info(f'执行 code 断言：{assert_text}')
        self._exec_code_assert(response, assert_text)

    def _json_asserter(self, response: dict, assert_text: dict) -> None:
        """
        **json 提取断言器**

        基本语法::
            1. $.key
            2. ...

        语法说明::
            符合 jsonpath 取值语法即可, `jsonpath <https://jg-rp.github.io/python-jsonpath/syntax/>`_

        取值范围::
            与 code 断言器一致

        一些简单的例子::
            1. $.status_code
            2. $.sql_data.username
            3. $.headers.*

        :param response:
        :param assert_text:
        :return:
        """
        if not isinstance(assert_text, dict):
            raise AssertSyntaxError('json 断言内容格式错误, 请检查断言脚本是否为 dict 格式')
        try:
            assert_check = assert_text['check']
            assert_value = assert_text['value']
            assert_type = assert_text['type']
            assert_jsonpath = assert_text['jsonpath']
        except KeyError as e:
            raise AssertSyntaxError(f'json 断言格式错误, 请检查: {e}')
        else:
            response_value = findall(assert_jsonpath, response)
            if response_value:
                log.info(f'执行 json 断言：{assert_text}')
                self._exec_json_assert(assert_check, assert_value, assert_type, response_value[0])
            else:
                raise JsonPathFindError(f'jsonpath 取值失败, 表达式: {assert_jsonpath}')

    def _sql_asserter(self, assert_text: dict) -> None:
        """
        **sql 提取断言器**

        提取方法与 json 断言器相同

        :param assert_text:
        :return:
        """
        if not isinstance(assert_text, dict):
            raise AssertSyntaxError('sql 断言内容格式错误, 请检查断言脚本是否为 dict 格式')
        try:
            assert_check = assert_text['check']
            assert_value = assert_text['value']
            assert_type = assert_text['type']
            assert_sql = assert_text['sql']
            assert_fetch = assert_text.get('fetch')
            assert_jsonpath = assert_text['jsonpath']
        except KeyError as e:
            raise AssertSyntaxError(f'SQL 断言格式错误, 请检查: {e}')
        else:
            if assert_sql.split(' ')[0].upper() != SqlType.select:
                raise AssertSyntaxError(f'SQL 断言 {assert_check}:{assert_type} 执行失败，请检查 SQL 是否为 DQL 类型')
            sql_data = mysql_client.exec_case_sql(assert_sql, assert_fetch)
            if not isinstance(sql_data, dict):
                raise JsonPathFindError('jsonpath 取值失败, SQL 语句执行结果不是有效的 dict 类型')
            sql_value = findall(assert_jsonpath, sql_data)
            if sql_value:
                log.info(f'执行 SQL 断言：{assert_text}')
                self._exec_json_assert(assert_check, assert_value, assert_type, sql_value[0])
            else:
                raise JsonPathFindError(f'jsonpath 取值失败, 表达式: {assert_jsonpath}')

    @staticmethod
    def _jsonschema_asserter(response: dict, assert_text: dict) -> None:
        """
        **jsonschema 断言器**

        提取方法与 json 断言器相同

        :param response:
        :param assert_text:
        :return:
        """
        if not isinstance(assert_text, dict):
            raise AssertSyntaxError('jsonschema 断言内容格式错误, 请检查断言脚本是否为 dict 格式')
        try:
            assert_check = assert_text['check']
            assert_type = assert_text['type']
            assert_jsonschema = assert_text['jsonschema']
        except KeyError as e:
            raise AssertSyntaxError(f'jsonschema 断言格式错误, 请检查: {e}')
        else:
            if assert_type != 'jsonschema':
                raise AssertSyntaxError('jsonschema 断言类型错误，类型必须为 "jsonschema"')
            log.info(f'执行 jsonschema 断言：{assert_text}')
            try:
                validate(response['json'], assert_jsonschema)
            except ValidationError as e:
                log.error(f'{assert_check or e}')
                raise e

    @staticmethod
    def _re_asserter(response: dict, assert_text: dict) -> None:
        """
        **正则断言器**

        :param response:
        :param assert_text:
        :return:
        """
        if not isinstance(assert_text, dict):
            raise AssertSyntaxError('正则断言内容格式错误, 请检查断言脚本是否为 dict 格式')
        try:
            assert_check = assert_text['check']
            assert_type = assert_text['type']
            assert_pattern = assert_text['pattern']
            assert_jsonpath = assert_text['jsonpath']
        except KeyError as e:
            raise AssertSyntaxError(f'正则断言格式错误, 请检查: {e}')
        else:
            if assert_type != 're':
                raise AssertSyntaxError('正则断言类型错误，类型必须为 "re"')
            response_value = findall(assert_jsonpath, response)
            if response_value:
                log.info(f'执行 re 断言：{assert_text}')
                result = re.match(assert_pattern, str(response_value[0]))
                if not result:
                    e = assert_check or '正则断言失败，响应内容与正则表达式不相符'
                    raise AssertionError(e)
            else:
                raise JsonPathFindError(f'jsonpath 取值失败, 表达式: {assert_jsonpath}')

    @staticmethod
    def _exec_code_assert(response: dict, assert_text: str) -> None:
        """
        执行 code 断言

        :param response:
        :param assert_text:
        :return:
        """
        assert_split = assert_text.split(' ')
        if not assert_text.startswith('assert '):
            raise AssertSyntaxError(f'code 断言取值表达式格式错误, 不符合语法规范: {assert_text}')
        if len(assert_split) < 4 or len(assert_split) > 6:
            raise AssertSyntaxError(f'code 断言取值表达式格式错误, 不符合语法规范: {assert_text}')
        else:

            def exec_assertion() -> None:
                """执行断言（闭包函数）"""
                get_code = pm_code.split('.')[2:]
                if len(get_code) == 1:
                    use_code = get_code[0]
                else:
                    use_code = '.'.join(get_code)
                # 如果断言有转型
                if use_code.endswith('))'):
                    use_code = use_code.replace('))', ')')
                if not use_code.startswith('get('):
                    raise AssertSyntaxError(
                        'code 断言取值表达式格式错误, 取值表达式条件不允许, 请在首位改用 get() 方法取值'
                    )
                else:
                    try:
                        response_value = eval(f'{response}.{use_code}')
                    except Exception as e:
                        err_msg = str(e.args).replace("'", '"').replace('\\', '')
                        raise AssertSyntaxError(f'code 断言取值表达式格式错误, {use_code} 取值失败, 详情: {err_msg}')
                    else:
                        # 执行断言
                        py_conversion_functions_exec_re = re.compile(
                            rf'(\b(?:{py_conversion_functions_re_str}))\((.*?)\)(?=[^)]*$)'  # noqa: ignore
                        )
                        format_assert_text = py_conversion_functions_exec_re.sub(
                            lambda x: x.group(1) + f'("""{response_value}""")', assert_text
                        )
                        if 'pm.response.get' in format_assert_text:
                            format_assert_text = format_assert_text.replace(pm_code, '{}', 1).format(response_value)
                        if len(assert_split) == 4:
                            # stdout 作为没有自定义断言错误时的信息补充
                            # 当断言错误触发时, 如果错误信息中包含自定义错误, 此项可忽略
                            log.warning('Warning: 此 code 断言未自定义错误提示信息')
                        if dirty_equals_assert:
                            exec('from dirty_equals import *')
                        exec(format_assert_text)

            py_conversion_functions_re_str = 'str|int|float|bool|list|tuple|set|dict'
            py_conversion_functions_pm_get_re = re.compile(rf'^({py_conversion_functions_re_str})\(pm\.response\.get')
            # 是否 dirty-equals 断言表达式
            dirty_equals_assert = True
            if not assert_split[1].startswith('pm.response.get'):
                if not py_conversion_functions_pm_get_re.match(assert_split[1]):
                    dirty_equals_assert = False
            if dirty_equals_assert:
                if assert_split[2] not in ['==', '!=']:
                    raise AssertSyntaxError(
                        f'code 断言取值表达式格式错误, 含有不支持的 dirty-equals 断言类型 {assert_split[2]}'
                    )
                # 处理比较值获取代码
                pm_code = assert_split[1]
                # 执行断言
                exec_assertion()
            else:
                assert_expr_type = ['==', '!=', '>', '<', '>=', '<=', 'in', 'not']
                if assert_split[2] not in assert_expr_type:
                    raise AssertSyntaxError(
                        f'code 断言表达式格式错误, 含有不支持的断言类型: {assert_split[2]}, 仅支持: {assert_expr_type}'
                    )
                else:
                    if assert_split[2] == 'not':
                        if assert_split[3] != 'in':
                            raise AssertSyntaxError(
                                f'code 断言表达式格式错误, 含有不支持的断言类型: {" ".join(assert_split[2:4])}'
                            )
                        else:
                            if not assert_split[4].startswith('pm.response.get'):
                                if not py_conversion_functions_pm_get_re.match(assert_split[4]):
                                    raise AssertSyntaxError(
                                        f'code 断言取值表达式格式错误, 含有不支持的断言取值表达式: {assert_split[4]}'
                                    )
                            # 如果包含自定义错误信息
                            if len(assert_split) == 6:
                                pm_code = assert_split[4].replace(',', '')
                            else:
                                pm_code = assert_split[4]
                    else:
                        # 非 dirty-equals 或 not in 断言表达式
                        if not assert_split[3].startswith('pm.response.get'):
                            if not py_conversion_functions_pm_get_re.match(assert_split[3]):
                                raise AssertSyntaxError(
                                    f'code 断言取值表达式格式错误, 含有不支持的断言取值表达式: {assert_split[3]}'
                                )
                        if len(assert_split) == 5:
                            pm_code = assert_split[3].replace(',', '')
                        else:
                            pm_code = assert_split[3]
                    # 执行断言
                    exec_assertion()

    @staticmethod
    def _exec_json_assert(assert_check: str | None, expected_value: Any, assert_type: str, actual_value: Any) -> None:
        """
        执行 jsonpath 断言

        :param assert_check:
        :param expected_value:
        :param assert_type:
        :param actual_value:
        :return:
        """
        if assert_type == AssertType.equal:
            assert expected_value == actual_value, (
                assert_check or f'预期结果: {Decimal(str(expected_value))} 不等于实际结果: {Decimal(str(actual_value))}'
            )

        elif assert_type == AssertType.not_equal:
            assert expected_value != actual_value, (
                assert_check or f'预期结果: {Decimal(str(expected_value))} 等于实际结果: {Decimal(str(actual_value))}'
            )

        elif assert_type == AssertType.greater_than:
            assert expected_value > actual_value, (
                assert_check or f'预期结果: {Decimal(str(expected_value))} 不大于实际结果: {Decimal(str(actual_value))}'
            )

        elif assert_type == AssertType.greater_than_or_equal:
            assert expected_value >= actual_value, (
                assert_check
                or f'预期结果: {Decimal(str(expected_value))} 不大于等于实际结果: {Decimal(str(actual_value))}'
            )

        elif assert_type == AssertType.less_than:
            assert expected_value < actual_value, (
                assert_check or f'预期结果: {Decimal(str(expected_value))} 不小于实际结果: {Decimal(str(actual_value))}'
            )

        elif assert_type == AssertType.less_than_or_equal:
            assert expected_value <= actual_value, (
                assert_check
                or f'预期结果: {Decimal(str(expected_value))} 不小于等于实际结果: {Decimal(str(actual_value))}'
            )

        elif assert_type == AssertType.string_equal:
            assert str(expected_value) == str(actual_value), (
                assert_check or f'预期结果(str): {str(expected_value)} 不等于实际结果(str): {str(actual_value)}'
            )

        elif assert_type == AssertType.length_equal:
            assert len(str(expected_value)) == len(str(actual_value)), (
                assert_check or f'预期结果: {str(expected_value)} 长度不等于实际结果: {str(actual_value)}'
            )

        elif assert_type == AssertType.not_length_equal:
            assert len(str(expected_value)) != len(str(actual_value)), (
                assert_check or f'预期结果: {str(expected_value)} 长度等于实际结果: {str(actual_value)}'
            )

        elif assert_type == AssertType.length_greater_than:
            assert len(str(expected_value)) > len(str(actual_value)), (
                assert_check or f'预期结果: {str(expected_value)} 长度不大于实际结果: {str(actual_value)}'
            )

        elif assert_type == AssertType.length_greater_than_or_equal:
            assert len(str(expected_value)) >= len(str(actual_value)), (
                assert_check or f'预期结果: {str(expected_value)} 长度不大于等于实际结果: {str(actual_value)}'
            )

        elif assert_type == AssertType.length_less_than:
            assert len(str(expected_value)) < len(str(actual_value)), (
                assert_check or f'预期结果: {str(expected_value)} 长度不小于实际结果: {str(actual_value)}'
            )

        elif assert_type == AssertType.length_less_than_or_equal:
            assert len(str(expected_value)) <= len(str(actual_value)), (
                assert_check or f'预期结果: {str(expected_value)} 长度不小于等于实际结果: {str(actual_value)}'
            )

        elif assert_type == AssertType.contains:
            assert str(expected_value) in str(actual_value), (
                assert_check or f'预期结果: {str(expected_value)} 不包含实际结果: {str(actual_value)}'
            )

        elif assert_type == AssertType.not_contains:
            assert str(expected_value) not in str(actual_value), (
                assert_check or f'预期结果: {str(expected_value)} 包含实际结果: {str(actual_value)}'
            )

        elif assert_type == AssertType.startswith:
            assert str(actual_value).startswith(str(expected_value)), (
                assert_check or f'实际结果: {str(actual_value)} 的开头不是预期结果: {str(expected_value)}'
            )

        elif assert_type == AssertType.endswith:
            assert str(actual_value).endswith(str(expected_value)), (
                assert_check or f'实际结果: {str(actual_value)} 的结尾不是预期结果: {str(expected_value)}'
            )

        else:
            raise ValueError(f'断言表达式格式错误, 含有不支持的断言类型: {assert_type}')

    def exec_asserter(self, response: dict, assert_text: str | dict | None) -> None:
        """
        根据断言内容自动选择断言器执行

        :param response:
        :param assert_text:
        :return:
        """
        if isinstance(assert_text, str):
            self._code_asserter(response, assert_text)
        elif isinstance(assert_text, dict):
            sql = assert_text.get('sql')
            jsonschema = assert_text.get('jsonschema')
            pattern = assert_text.get('pattern')
            if sql:
                self._sql_asserter(assert_text)
            elif jsonschema:
                self._jsonschema_asserter(response, assert_text)
            elif pattern:
                self._re_asserter(response, assert_text)
            else:
                self._json_asserter(response, assert_text)
        else:
            raise AssertSyntaxError(f'断言表达式格式错误: {assert_text}')


asserter = Asserter()
