#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re

from typing import Any

from httpfpt.common.log import log
from httpfpt.enums.setup_type import SetupType
from httpfpt.enums.teardown_type import TeardownType


class HookExecutor:
    def __init__(self) -> None:
        # hook 开头: a-zA-Z_
        # hook 表达: ${func()} 或 ${func(1, 2)}
        self.func_re = re.compile(r'\${([a-zA-Z_]\w*\([$\w.\-/\s=,]*\))}')

    def hook_func_value_replace(self, target: dict) -> Any:
        """
        执行除前后置 hook 以外的所有 hook 函数并替换为它的返回值

        :param target:
        :return:
        """
        # 数据排除
        setup = target['test_steps'].get('setup')
        teardown = target['test_steps'].get('teardown')
        setup_hooks_with_index = []
        teardown_hooks_with_index = []
        if setup:
            setup_hooks_with_index.extend(
                [(i, item) for i, item in enumerate(setup) if item.get(SetupType.HOOK) is not None]
            )
            if setup_hooks_with_index:
                target['test_steps']['setup'] = [
                    item for item in target['test_steps']['setup'] if item.get(SetupType.HOOK) is None
                ]
        if teardown:
            teardown_hooks_with_index.extend(
                [(i, item) for i, item in enumerate(teardown) if item.get(TeardownType.HOOK) is not None]
            )
            if teardown_hooks_with_index:
                target['test_steps']['teardown'] = [
                    item for item in target['test_steps']['teardown'] if item.get(TeardownType.HOOK) is None
                ]

        str_target = json.dumps(target, ensure_ascii=False)

        match = self.func_re.search(str_target)
        if not match:
            return target

        # hook 返回值替换
        exec('from httpfpt.data.hooks import *')
        for match in self.func_re.finditer(str_target):
            hook_key = match.group(1)
            try:
                # locals() 获取到执行函数内所有变量并以字典形式返回
                loc = locals()
                exec(f'result = {hook_key}')
                value = str(loc['result'])
                str_target = self.func_re.sub(value, str_target, 1)
                log.info(f'请求数据函数 {hook_key} 返回值替换完成')
            except Exception as e:
                log.error(f'请求数据函数 {hook_key} 返回值替换失败: {e}')
                raise e

        dict_target = json.loads(str_target)

        # 数据还原
        if setup:
            if setup_hooks_with_index:
                for i, item in setup_hooks_with_index:
                    target['test_steps']['setup'].insert(i, item)
        if teardown:
            if teardown_hooks_with_index:
                for i, item in teardown_hooks_with_index:
                    target['test_steps']['teardown'].insert(i, item)

        return dict_target

    def exec_hook_func(self, hook_var: str) -> None:
        """
        执行 hook 函数不返回任何值

        :param hook_var:
        :return:
        """
        key = self.func_re.search(hook_var)
        func = key.group(1)
        exec('from httpfpt.data.hooks import *')
        log.info(f'执行 hook：{func}')
        exec(func)

    @staticmethod
    def exec_any_code(code: str) -> bool:
        """
        执行任何函数

        :param code:
        :return:
        """
        exec('import os')
        exec('import sys')
        result = eval(code)
        log.info(f'执行代码：{code}')
        return result


hook_executor = HookExecutor()
