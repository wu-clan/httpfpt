#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def code_asserter(response: dict, assert_text: str) -> None:
    """
    **代码断言器, 像 pytest 断言一样使用它**


    *目前支持的表达式*::

        - assert 期望值 条件 pm.response.get()... 错误信息[可选]
        - assert pm.response.startswith()
        - assert pm.response.endswith()

    *比较值说明*::

            与 postman 相似, 但又完全不同, 你只能通过全程手动脚本来控制断言数据, 并且, 需要以 pm.response 作为比较值的开头,
        后面获取的内容中, 需要以 .get() 为基础, 视情况添加 python 代码可以简单实现的方法

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
    if not assert_text.startswith('assert '):
        raise ValueError('断言比较表达式格式错误, 必须以 assert 开头')
    if len(assert_text.split(' ')) < 2:
        raise ValueError('断言比较表达式格式错误, 却少条件语句')
    elif len(assert_text.split(' ')) == 2:
        if not assert_text.split(' ')[1].startswith('pm.response'):
            raise ValueError(f'断言比较表达式格式错误, 含有不支持的断言条件: {assert_text.split(" ")[1]}')
        exec(assert_text)
    elif len(assert_text.split(' ')) > 2:
        if assert_text.split(' ')[2] not in ['==', '!=', '>', '<', '>=', '<=', 'in']:
            raise ValueError(f'断言比较表达式格式错误, 含有不支持的断言条件: {assert_text.split(" ")[2]}')
        if not assert_text.split(' ')[3].startswith('pm.response'):
            raise ValueError('断言比较表达式格式错误, 比较表达式必须以 pm.response 开头')
        if len(assert_text.split(' ')) >= 5:
            pm_code = assert_text.split(' ')[3].replace(',', '')
        else:
            pm_code = assert_text.split(' ')[3]
        get_code = pm_code.split('.')[2:]
        use_code = None
        if len(get_code) < 1:
            raise ValueError('断言比较表达式格式错误, 比较表达式缺少执行条件')
        if len(get_code) == 1:
            use_code = get_code[0]
        if len(get_code) > 1:
            use_code = '.'.join(get_code)
        if not use_code.startswith('get('):
            raise ValueError('断言比较表达式格式错误, 比较表达式条件不允许, 请使用 get() 方法取值')
        else:
            try:
                get_response_value = eval(f'{response}.{use_code}')
            except Exception as e:
                err_msg = str(e.args).replace("\'", '"').replace('\\', '')
                raise ValueError(f'断言比较表达式格式错误, {use_code} 取值失败, 详情:{err_msg}')
            else:
                if len(assert_text.split(' ')) >= 5:
                    pm_code = assert_text.split(' ')[-2].replace(',', '')
                else:
                    pm_code = assert_text.split(' ')[-1]
                end_assert_result = assert_text.replace(pm_code, '{}', 1).format(get_response_value)
                try:
                    exec(end_assert_result)
                except Exception as e:
                    raise ValueError(f'断言表达式错误, 错误信息: {e}')


def json_asserter(response: dict, assert_text: dict) -> None:
    # todo
    ...


if __name__ == '__main__':
    code_asserter({"status_code": 200, "msg": "success"}, "assert 200 == pm.response.get('status_code')")
    code_asserter({"status_code": 20, "msg": "success"}, "assert 'fail' in pm.response")
    code_asserter({"status_code": 2}, "assert 2 == pm.response.get('status_code').get('test'), 'err'")
    code_asserter({"status_code": 2}, "assert 200 == pm.response.get('status_code'), 'err'")
