#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from decimal import Decimal
from typing import Union, Any

from jsonpath import jsonpath

from httpfpt.common.log import log
from httpfpt.db.mysql_db import MysqlDB
from httpfpt.enums.assert_type import AssertType


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
              "url": '',
              "status_code": 200,
              "elapsed": 0,
              "headers": {},
              "cookies": {},
              "result": {},
              "content": {},
              "text": {},
              "stat": {
                "execute_time": "None"
              },
              "sql_data": {}
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
        log.info(f'执行断言：{assert_text}')
        self._exec_code_assert(response, assert_text)

    def _json_asserter(self, response: dict, assert_text: dict) -> None:
        """
        **json 提取断言器**

        基本语法::
            1. $.key
            2. ...

        语法说明::
            符合 jsonpath 取值语法即可, `jsonpath <https://goessner.net/articles/JsonPath/index.html#e2>`_

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
            raise ValueError('断言内容格式错误, 请检查断言脚本是否为 dict 格式')
        try:
            assert_check = assert_text['check']
            assert_value = assert_text['value']
            assert_type = assert_text['type']
            assert_jsonpath = assert_text['jsonpath']
        except KeyError as e:
            raise ValueError(f'断言格式错误, 缺少必须参数, 请检查: {e}')
        else:
            response_value = jsonpath(response, assert_jsonpath)
        if response_value:
            log.info(f'执行断言：{assert_text}')
            self._exec_json_assert(assert_check, assert_value, assert_type, response_value[0])
        else:
            raise ValueError(f'jsonpath取值失败, 表达式: {assert_jsonpath}')

    def _sql_asserter(self, assert_text: dict) -> None:
        """
        **sql 提取断言器**

        提取方法与 json 断言器相同

        :param assert_text:
        :return:
        """
        if not isinstance(assert_text, dict):
            raise ValueError('断言内容格式错误, 请检查断言脚本是否为 dict 格式')
        try:
            assert_check = assert_text['check']
            assert_value = assert_text['value']
            assert_type = assert_text['type']
            assert_sql = assert_text['sql']
            assert_jsonpath = assert_text['jsonpath']
        except KeyError as e:
            raise ValueError(f'断言格式错误, 缺少必须参数, 请检查: {e}')
        else:
            sql_data = MysqlDB().exec_case_sql(assert_sql)
            sql_value = jsonpath(sql_data, assert_jsonpath)
        if sql_value:
            log.info(f'执行断言：{assert_text}')
            self._exec_json_assert(assert_check, assert_value, assert_type, sql_value[0])
        else:
            raise ValueError(f'jsonpath取值失败, 表达式: {assert_jsonpath}')

    @staticmethod
    def _exec_code_assert(response: dict, assert_text: str) -> None:
        """
        执行 code 断言

        :param response:
        :param assert_text:
        :return:
        """
        assert_split = assert_text.split(' ')
        if assert_text.startswith("'{") or assert_text.startswith("'["):
            raise ValueError('code 断言内容语法错误, 请查看是否为 str / list 类型, 并检查断言语法是否规范')
        if not assert_text.startswith('assert '):
            raise ValueError(f'断言取值表达式格式错误, 不符合语法规范: {assert_text}')
        if len(assert_split) < 4 or len(assert_split) > 6:
            raise ValueError(f'断言取值表达式格式错误, 不符合语法规范: {assert_text}')
        else:
            # 是否 dirty-equals 断言表达式
            if assert_split[1].startswith('pm.response.get'):
                if assert_split[2] not in ['==', '!=']:
                    raise ValueError(f'断言取值表达式格式错误, 含有不支持的断言类型 {assert_split[2]}')
                if not assert_split[3].startswith('Is'):
                    raise ValueError('断言取值表达式格式错误, 不符合 dirty-equals 断言表达式规范')
                # 处理比较值获取代码
                pm_code = assert_split[1]
                get_code = pm_code.split('.')[2:]
                if len(get_code) == 1:
                    use_code = get_code[0]
                else:
                    use_code = '.'.join(get_code)
                # 如果断言有转型
                if use_code.endswith('))'):
                    use_code = use_code.replace('))', ')')
                if not use_code.startswith('get('):
                    raise ValueError('断言取值表达式格式错误, 取值表达式条件不允许, 请在首位改用 get() 方法取值')
                else:
                    try:
                        response_value = eval(f'{response}.{use_code}')
                    except Exception as e:
                        err_msg = str(e.args).replace("\'", '"').replace('\\', '')
                        raise ValueError(f'断言取值表达式格式错误, {use_code} 取值失败, 详情: {err_msg}')
                    else:
                        # 执行断言
                        format_assert_text = assert_text.replace(pm_code, '{}', 1).format(response_value)
                        if len(assert_split) == 4:
                            # stdout 作为没有自定义断言错误时的信息补充
                            # 当断言错误触发时, 如果错误信息中包含自定义错误, 此项可忽略
                            print('Warning: 未自定义断言错误信息的断言:')
                            print(f'-> {format_assert_text}')
                        exec('from dirty_equals import *')
                        exec(format_assert_text)
            else:
                assert_expr_type = ['==', '!=', '>', '<', '>=', '<=', 'in', 'not']
                if assert_split[2] not in assert_expr_type:
                    raise ValueError(f'断言表达式格式错误, 含有不支持的断言类型: {assert_split[2]}, 仅支持: {assert_expr_type}')  # noqa: E501
                else:
                    if assert_split[2] == 'not':
                        if assert_split[3] != 'in':
                            raise ValueError(f'断言表达式格式错误, 含有不支持的断言类型: {" ".join(assert_split[2:4])}')
                        else:
                            if 'pm.response.get' not in assert_split[4]:
                                raise ValueError(f'断言取值表达式格式错误, 含有不支持的取值表达式: {assert_split[4]}')
                            # 如果包含自定义错误信息
                            if len(assert_split) == 6:
                                pm_code = assert_split[4].replace(',', '')
                            else:
                                pm_code = assert_split[4]
                    else:
                        # 非 dirty-equals 或 not in 断言表达式
                        if 'pm.response.get' not in assert_split[3]:
                            raise ValueError(f'断言取值表达式格式错误, 含有不支持的取值表达式: {assert_split[3]}')
                        if len(assert_split) == 5:
                            pm_code = assert_split[3].replace(',', '')
                        else:
                            pm_code = assert_split[3]
                    # 处理取值代码执行断言
                    get_code = pm_code.split('.')[2:]
                    if len(get_code) == 1:
                        use_code = get_code[0]
                    else:
                        use_code = '.'.join(get_code)
                    if use_code.endswith('))'):
                        use_code = use_code.replace('))', ')')
                    if not use_code.startswith('get('):
                        raise ValueError('断言取值表达式格式错误, 取值表达式条件不允许, 请在首位改用 get() 方法取值')
                    else:
                        try:
                            response_value = eval(f'{response}.{use_code}')
                        except Exception as e:
                            err_msg = str(e.args).replace("\'", '"').replace('\\', '')
                            raise ValueError(f'断言取值表达式格式错误, {use_code} 取值失败, 详情: {err_msg}')
                        else:
                            # 执行断言
                            format_assert_text = assert_text.replace(pm_code, '{}', 1).format(response_value)
                            if len(assert_split) == 4:
                                # stdout 作为没有自定义断言错误时的信息补充
                                # 当断言错误触发时, 如果错误信息中包含自定义错误, 此项可忽略
                                print('Warning: 未自定义断言错误信息的断言:')
                                print(f'-> {format_assert_text}')
                            exec(format_assert_text)

    @staticmethod
    def _exec_json_assert(
        assert_check: Union[str, None], expected_value: Any, assert_type: str, actual_value: Any
    ) -> None:
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
                or f'预期结果: {Decimal(str(expected_value))} 不大于等于实际结果: {Decimal(str(actual_value))}'  # noqa: E501
            )

        elif assert_type == AssertType.less_than:
            assert expected_value < actual_value, (
                assert_check or f'预期结果: {Decimal(str(expected_value))} 不小于实际结果: {Decimal(str(actual_value))}'
            )

        elif assert_type == AssertType.less_than_or_equal:
            assert expected_value <= actual_value, (
                assert_check
                or f'预期结果: {Decimal(str(expected_value))} 不小于等于实际结果: {Decimal(str(actual_value))}'  # noqa: E501
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

    def exec_asserter(self, response: dict, assert_text: Union[str, list, dict, None]) -> None:
        """
        根据断言内容自动选择断言器执行

        :param response:
        :param assert_text:
        :return:
        """
        if not assert_text:
            ...
        elif isinstance(assert_text, str):
            self._code_asserter(response, assert_text)
        elif isinstance(assert_text, list):
            for text in assert_text:
                if isinstance(text, str):
                    self._code_asserter(response, text)
                elif isinstance(text, dict):
                    if text.get('sql') is None:
                        self._json_asserter(response, text)
                    else:
                        self._sql_asserter(text)
                else:
                    raise ValueError(f'断言表达式格式错误: {text}')
        else:
            raise ValueError(f'断言表达式格式错误: {assert_text}')
