#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

from fastpt.common.log import log
from fastpt.common.yaml_operate import read_yaml
from fastpt.core.path_conf import YAML_VARS_PATH


class VarsExtractor:

    def __init__(self):
        # 变量表达: ${var} 或 $var
        # hooks 表达: ${func()} 或 ${func(1, 2)}
        # 变量和 hooks 开头: a-zA-Z_
        self.regular_re = r'\${([a-zA-Z_]\w*)\}|\${([a-zA-Z_]\w*\([\$\w\.\-/\s=,]*\))}|\$([a-zA-Z_]\w*)'

    def vars_replace(self, target):
        """
        变量替换

        :param target:
        :return:
        """
        str_target = target
        if target is not None:
            if not isinstance(target, str):
                str_target = str(target)

        # 获取所有自定义全局变量
        read_vars = read_yaml(YAML_VARS_PATH, filename='global_vars.yml')

        while re.findall(self.regular_re, str_target):
            keys = re.search(self.regular_re, str_target)
            key = keys.group(1) or keys.group(2) or keys.group(3)
            try:
                value = str(read_vars[f'{key}'])
                str_target = re.sub(self.regular_re, value, str_target, 1)
            except KeyError:
                value = str(self.exec_func(key))
                str_target = re.sub(self.regular_re, value, str_target, 1)
            except NameError as e:
                log.error('未在全局参数和hooks中找到: %s, 请检查变量名或函数名是否正确' % key)
                raise e
            except Exception as e:
                log.error('请求数据内变量替换错误')
                raise e
        return str_target

    @staticmethod
    def exec_func(func: str):
        """
        执行 hooks 函数

        :param func: 函数名
        :return:
        """
        # locals() 获取到执行函数内所有变量并以字典形式返回
        loc = locals()
        exec('from fastpt.data.hooks import *')
        exec(f'result = {func}')
        return loc['result']
