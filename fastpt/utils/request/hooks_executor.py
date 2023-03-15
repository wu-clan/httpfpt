#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from typing import Any, NoReturn, Union

from fastpt.common.log import log


class HookExecutor:

    def __init__(self):
        # hooks 表达: ${func()} 或 ${func(1, 2)}
        # hooks 开头: a-zA-Z_
        self.func_re = r'\${([a-zA-Z_]\w*\([\$\w\.\-/\s=,]*\))}'

    def hook_func_extract(self, target: Union[list, str]) -> list:
        """
        提取用例中的函数

        :return:
        """
        hook_list = []
        str_target = str(target)
        while re.findall(self.func_re, str_target):
            key = re.search(self.func_re, str_target)
            hook_key = key.group(1)
            if hook_key is not None:
                hook_list.append(hook_key)
                str_target = str_target.replace(hook_key, '')
        return hook_list

    def hook_func_value_replace(self, target: dict) -> Any:
        """
        执行 hook 函数并替换为返回值

        :param target:
        :return:
        """
        str_target = str(target)
        exec('from fastpt.data.hooks import *')
        while re.findall(self.func_re, str_target):
            key = re.search(self.func_re, str_target)
            hook_key = key.group(1)
            try:
                # locals() 获取到执行函数内所有变量并以字典形式返回
                loc = locals()
                exec(f'result = {hook_key}')
                value = str(loc['result'])
                str_target = re.sub(self.func_re, value, str_target, 1)
                log.info(f'请求数据函数 {hook_key} 返回值替换完成')
            except Exception as e:
                log.error(f'请求数据函数 {hook_key} 返回值替换失败: {e}')
                raise e

        dict_target = eval(str_target)

        return dict_target

    def exec_hook_func(self, func_list: list) -> NoReturn:
        """
        执行 hook 函数不返回任何值

        :param func_list:
        :return:
        """
        func_list = self.hook_func_extract(func_list)
        exec('from fastpt.data.hooks import *')
        for func in func_list:
            log.info(f'执行 hook：{func}')
            exec(func)
