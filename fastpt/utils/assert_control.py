#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Union

from jsonpath import jsonpath

from fastpt.schema.assert_type import AssertType


class Asserter:

    def _code_asserter(self, response: dict, assert_text: Union[str, list]) -> None:
        """
        **代码断言器, 像 pytest 断言一样使用它**

        --

        *基本表达式*::

            1. assert 期望值 条件 比较表达式(pm.response.get()...), 错误信息(可选, 如果不填写, 记得去掉前面的逗号)
            2. assert pm.response.startswith()
            3. assert pm.response.endswith()
            4. assert pm.response...
            ...

        *比较值说明*::

                与 postman 相似, 但又完全不同, 你只能通过全程手动脚本来控制断言数据, 并且, 需要以 pm.response 作为比较值的开头,
            后面获取的内容中, 需要以 .get() 为基础, 视情况添加 python 代码的一些简单方法并确保它们符合常规 assert 语法

        *比较直取值范围*::

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

        *一些简单的例子*::

            1. assert 200 == pm.response.get('status_code')
            2. assert 'success' != pm.response.get('msg')[1]
            3. assert 'com' in pm.response..get('content').get('url')

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

        --

        *基本表达式*::

            pm.response...

        *表达式说明*::

            首先, 需要以 $. 开头, 后面的内容是你从 json 中通过 jsonpath 语法获取的,
            语法在这里: https://goessner.net/articles/JsonPath/index.html#e2

        *取值范围*::

            同代码断言其

        *一些简单的例子*::

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
        if not assert_text.startswith('assert '):
            raise ValueError('断言比较表达式格式错误, 必须以 assert 开头')
        if len(assert_text.split(' ')) < 2:
            raise ValueError('断言比较表达式格式错误, 却少条件语句')
        elif len(assert_text.split(' ')) == 2:
            if not assert_text.split(' ')[1].startswith('pm.response'):
                raise ValueError(f'断言表达式格式错误, 含有不支持的断言条件: {assert_text.split(" ")[1]}')
            # 简约型脚本直接运行
            exec(assert_text)
        else:
            # 处理断言类型及比较值
            if assert_text.split(' ')[2] not in ['==', '!=', '>', '<', '>=', '<=', 'in', 'not']:
                raise ValueError(f'断言表达式格式错误, 含有不支持的断言类型: {assert_text.split(" ")[2]}')
            if assert_text.split(' ')[2] == 'not':
                if assert_text.split(' ')[3] != 'in':
                    raise ValueError(f'断言表达式格式错误, 含有不支持的断言类型: {" ".join(assert_text.split(" ")[2:4])}')
                else:
                    if not assert_text.split(' ')[4].startswith('pm.response'):
                        raise ValueError(
                            f'断言比较表达式格式或断言条件错误, 含有不支持的条件语句 {assert_text.split(" ")[3]}'
                            f'比较表达式必须以 pm.response 开头'
                        )
                    if len(assert_text.split(' ')) >= 6:
                        pm_code = assert_text.split(' ')[4].replace(',', '')
                    else:
                        pm_code = assert_text.split(' ')[4]
            else:
                if not assert_text.split(' ')[3].startswith('pm.response'):
                    raise ValueError(
                        f'断言比较表达式格式或断言条件错误, 含有不支持的条件语句 {assert_text.split(" ")[3]}'
                        f'比较表达式必须以 pm.response 开头'
                    )
                if len(assert_text.split(' ')) >= 5:
                    pm_code = assert_text.split(' ')[3].replace(',', '')
                else:
                    pm_code = assert_text.split(' ')[3]
            # 处理比较值获取代码
            get_code = pm_code.split('.')[2:]
            if len(get_code) < 1:
                raise ValueError('断言比较表达式格式错误, 比较表达式缺少执行条件')
            elif len(get_code) == 1:
                use_code = get_code[0]
            else:
                use_code = '.'.join(get_code)
            if not use_code.startswith('get('):
                raise ValueError('断言比较表达式格式错误, 比较表达式条件不允许, 请使用 get() 方法取值')
            else:
                try:
                    response_value = eval(f'{response}.{use_code}')
                except Exception as e:
                    err_msg = str(e.args).replace("\'", '"').replace('\\', '')
                    raise ValueError(f'断言比较表达式格式错误, {use_code} 取值失败, 详情: {err_msg}')
                else:
                    if len(assert_text.split(' ')) >= 5:
                        pm_code = assert_text.split(' ')[-2].replace(',', '')
                    else:
                        pm_code = assert_text.split(' ')[-1]
                    end_assert_result = assert_text.replace(pm_code, '{}', 1).format(response_value)
                    try:
                        exec(end_assert_result)
                    except Exception as e:
                        raise ValueError(f'断言表达式错误, 错误信息: {e}')

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
        执行断言器

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
