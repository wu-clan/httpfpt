#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Union

from jsonpath import jsonpath

from fastpt.schema.assert_type import AssertType


class Asserter:

    def _code_asserter(self, response: dict, assert_text: Union[str, list]) -> None:
        """
        **代码断言器, 像 pytest 断言一样使用它**

        基本语法::
            1. assert 期望值 条件 取值表达式(pm.response.get()...), 错误信息(可选, 如果不填写, 记得去掉前面的逗号)
            2. assert 取值表达式

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
            4. assert pm.response.get('header').get('fastpt') == IsDict(version=0.0.1)
            5. assert pm.response.get('content').get('id') == IsUUID

        :param response:
        :param assert_text:
        :return:
        """
        if isinstance(assert_text, str):
            self._exec_code_assert(response, assert_text)
        elif isinstance(assert_text, list):
            for a in assert_text:
                self._exec_code_assert(response, a)
        else:
            raise ValueError('断言内容格式错误, 请检查断言脚本是否为 str / list 格式')

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
        for k, v in assert_text.items():
            try:
                assert_value = assert_text[k]['value']
                assert_type = assert_text[k]['type']
                assert_jsonpath = assert_text[k]['jsonpath']
            except KeyError as e:
                raise ValueError(f'断言格式错误, 缺少必须参数, 请检查: {e}')
            else:
                response_value = jsonpath(response, assert_jsonpath)
            if response_value:
                self._exec_json_assert(assert_value, assert_type, response_value[0])
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
            raise ValueError('断言内容格式错误, 使用了为解析的数据')
        if not assert_text.startswith('assert '):
            raise ValueError('断言取值表达式格式错误, 必须以 assert 开头')
        if len(assert_split) < 2:
            raise ValueError('断言取值表达式格式错误, 却少条件语句')
        elif len(assert_split) == 2:
            if not assert_split[1].startswith('pm.response.get'):
                raise ValueError(
                    f'断言表达式格式错误, 含有不支持的断言类型: {assert_split[1]} '
                    f'取值表达式必须以 pm.response.get 开头并使用 get() 方法取值, 首位暂不支持下标取值方式'
                )
            # 简约型脚本直接运行
            exec(assert_text)
        elif len(assert_split) > 6:
            raise ValueError('断言取值表达式格式错误, 不符合语法规范')
        else:
            # 是否 dirty-equals 断言表达式
            if assert_split[1].startswith('pm.response.get'):
                if assert_split[2] not in ['==', '!=']:
                    raise ValueError(f'断言取值表达式格式错误, 含有不支持的断言类型 {assert_split[2]}')
                if not assert_split[3].startswith('Is'):
                    raise ValueError('断言取值表达式格式错误, 不符合 dirty-equals 断言表达式规范')
                if len(assert_split) != 4:
                    raise ValueError('断言取值表达式格式错误, 不符合 dirty-equals 断言表达式规范')
                # 处理比较值获取代码
                pm_code = assert_split[1]
                get_code = pm_code.split('.')[2:]
                if len(get_code) < 1:
                    raise ValueError('断言取值表达式格式错误, 取值表达式缺少执行条件')
                elif len(get_code) == 1:
                    use_code = get_code[0]
                else:
                    use_code = '.'.join(get_code)
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
                        exec('from dirty_equals import *')
                        exec(format_assert_text)
            else:
                if assert_split[2] not in ['==', '!=', '>', '<', '>=', '<=', 'in', 'not']:
                    raise ValueError(f'断言表达式格式错误, 含有不支持的断言类型: {assert_split[2]}')
                else:
                    if assert_split[2] == 'not':
                        if assert_split[3] != 'in':
                            raise ValueError(f'断言表达式格式错误, 含有不支持的断言类型: {" ".join(assert_split[2:4])}')
                        else:
                            if not assert_split[4].startswith('pm.response.get'):
                                raise ValueError(
                                    f'断言取值表达式格式或断言类型错误, 含有不支持的条件语句 {assert_split[3]} '
                                    f'取值表达式必须以 pm.response.get 开头并使用 get() 方法取值, 首位暂不支持下标取值方式'
                                )
                            # 如果包含自定义错误信息
                            if len(assert_split) == 6:
                                pm_code = assert_split[4].replace(',', '')
                            else:
                                pm_code = assert_split[4]
                    else:
                        # 非 dirty-equals 或 not in 断言表达式
                        if not assert_split[3].startswith('pm.response.get'):
                            raise ValueError(
                                f'断言取值表达式格式或断言类型错误, 含有不支持的条件语句 {assert_split[3]}'
                                f'取值表达式必须以 pm.response.get 开头并使用 get() 方法取值, 首位暂不支持下标取值方式'
                            )
                        if len(assert_split) == 5:
                            pm_code = assert_split[3].replace(',', '')
                        else:
                            pm_code = assert_split[3]
                    # 处理取值代码执行断言
                    get_code = pm_code.split('.')[2:]
                    if len(get_code) < 1:
                        raise ValueError('断言取值表达式格式错误, 取值表达式缺少执行条件')
                    elif len(get_code) == 1:
                        use_code = get_code[0]
                    else:
                        use_code = '.'.join(get_code)
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
                            exec(format_assert_text)

    @staticmethod
    def _exec_json_assert(expected_value, assert_type: str, actual_value) -> None:
        """
        执行 jsonpath 断言

        :param expected_value:
        :param assert_type:
        :param actual_value:
        :return:
        """
        if assert_type == AssertType.equal:
            assert expected_value == actual_value
        elif assert_type == AssertType.not_equal:
            assert expected_value != actual_value
        elif assert_type == AssertType.greater_than:
            assert expected_value > actual_value
        elif assert_type == AssertType.greater_than_or_equal:
            assert expected_value >= actual_value
        elif assert_type == AssertType.less_than:
            assert expected_value < actual_value
        elif assert_type == AssertType.less_than_or_equal:
            assert expected_value <= actual_value
        elif assert_type == AssertType.string_equal:
            assert str(expected_value) == str(actual_value)
        elif assert_type == AssertType.length_equal:
            assert len(str(expected_value)) == len(str(actual_value))
        elif assert_type == AssertType.not_length_equal:
            assert len(str(expected_value)) != len(str(actual_value))
        elif assert_type == AssertType.length_greater_than:
            assert len(str(expected_value)) > len(str(actual_value))
        elif assert_type == AssertType.length_greater_than_or_equal:
            assert len(str(expected_value)) >= len(str(actual_value))
        elif assert_type == AssertType.length_less_than:
            assert len(str(expected_value)) < len(str(actual_value))
        elif assert_type == AssertType.length_less_than_or_equal:
            assert len(str(expected_value)) <= len(str(actual_value))
        elif assert_type == AssertType.contains:
            assert str(expected_value) in str(actual_value)
        elif assert_type == AssertType.not_contains:
            assert str(expected_value) not in str(actual_value)
        elif assert_type == AssertType.startswith:
            assert str(expected_value).startswith(str(actual_value))
        elif assert_type == AssertType.endswith:
            assert str(expected_value).endswith(str(actual_value))
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
        elif isinstance(assert_text, dict):
            self._json_asserter(response, assert_text)
        else:
            self._code_asserter(response, assert_text)
