#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from typing import Any


class HookExecutor:

    def __init__(self):
        # hooks 表达: ${func()} 或 ${func(1, 2)}
        self.func_re = r'\${([a-zA-Z_]\w*\([\$\w\.\-/\s=,]*\))}'

    def case_func_extract(self, target: list) -> list:
        """
        提取用例中的函数

        :return:
        """
        hook_list = []
        str_target = str(target)
        while re.findall(self.func_re, str_target):
            key = re.search(self.func_re, str_target)
            hook_key = key.group(1)
            hook_list.append(hook_key)
        return hook_list

    @staticmethod
    def exec_func(func: str) -> Any:
        """
        执行 hook 函数

        :param func: 函数名
        :return:
        """
        # locals() 获取到执行函数内所有变量并以字典形式返回
        loc = locals()
        exec('from fastpt.data.hooks import *')
        exec(f'result = {func}')
        return loc['result']

    def exec_case_func(self, func_list: list) -> None:
        """
        执行用例中的 hook 函数

        :param func_list:
        :return:
        """
        func_list = self.case_func_extract(func_list)
        loc = locals()
        for func in func_list:
            exec('from fastpt.data.hooks import *')
            exec(f'result = {func}')
