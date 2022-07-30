#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os.path
import re
from typing import Union

from fastpt.common.log import log
from fastpt.common.variable_cache import VariableCache
from fastpt.common.yaml_operate import read_yaml
from fastpt.core.path_conf import TEST_DATA_PATH, RUN_ENV_PATH
from fastpt.utils.env_control import get_env_dict


class VarsExtractor:

    def __init__(self):
        # 变量表达: ${var} 或 $var
        # hooks 表达: ${func()} 或 ${func(1, 2)}
        # 变量和 hooks 开头: a-zA-Z_
        self.regular_re = r'\$([a-zA-Z_]\w*)|\${([a-zA-Z_]\w*)\}|\${([a-zA-Z_]\w*\([\$\w\.\-/\s=,]*\))}'

    def _vars_replace(self, target):
        """
        变量替换, 老版本, 仅作保留

        :param target:
        :return:
        """
        str_target = target
        if target is not None:
            if not isinstance(target, str):
                str_target = str(target)

        # 获取所有自定义全局变量
        read_vars = read_yaml(TEST_DATA_PATH, filename='global_vars.yaml')

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

    def new_vars_replace(self, target) -> Union[str, None]:
        """
        变量替换, 新版本更换为 re.match() 来强制约束变量的使用

        :param target:
        :return:
        """
        # 获取临时变量实例
        cache_vars = VariableCache()

        # 获取所有环境变量
        try:
            env = target['config']['request']['env']
        except KeyError:
            raise ValueError('测试环境获取失败, 测试用例缺少 config:request:env 参数')
        if not isinstance(env, str):
            raise ValueError('测试环境获取失败, 请使用合法的环境配置')
        try:
            env_file = os.path.join(RUN_ENV_PATH, env)
            env_vars = get_env_dict(env_file)
        except OSError:
            raise ValueError('测试环境获取失败, 请检查测试用例环境配置')

        # 获取所有自定义全局变量
        read_vars = read_yaml(TEST_DATA_PATH, filename='global_vars.yaml')

        # 获取变量
        str_target = target
        if str_target is None:
            return str_target

        if not isinstance(target, str):
            str_target = str(target)

        keys = re.match(self.regular_re, str_target)
        var_key = keys.group(1) or keys.group(2)
        hook_key = keys.group(3)

        # 替换: 临时变量 > 环境变量 > 全局变量
        if var_key is not None:
            value = cache_vars.get(var_key)
            if value is None:
                try:
                    value = str(env_vars[f'{var_key}'])
                    str_target = re.sub(self.regular_re, value, str_target, 1)
                except KeyError:
                    value = str(read_vars[f'{var_key}'])
                    str_target = re.sub(self.regular_re, value, str_target, 1)
                except Exception as e:
                    log.error('请求数据变量"{}"替换失败: {}'.format(var_key, e))
                    raise e

        if hook_key is not None:
            try:
                value = str(self.exec_func(hook_key))
                str_target = re.sub(self.regular_re, value, str_target, 1)
            except Exception as e:
                log.error('请求数据hook"%s"替换失败: %s' % hook_key, e)
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
