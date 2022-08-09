#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os.path
import re
from typing import Union

from jsonpath import jsonpath

from fastpt.common.env_handler import get_env_dict, write_env_vars
from fastpt.common.log import log
from fastpt.common.variable_cache import VariableCache
from fastpt.common.yaml_handler import read_yaml, write_yaml_vars
from fastpt.core.path_conf import TEST_DATA_PATH, RUN_ENV_PATH


class VarsExtractor:

    def __init__(self):
        # 变量表达: ${var} 或 $var
        # 变量和 hooks 开头: a-zA-Z_
        self.vars_re = r'\$([a-zA-Z_]\w*)|\${([a-zA-Z_]\w*)\}'

    def vars_replace(self, target) -> Union[dict, None]:
        """
        变量替换

        :param target:
        :return:
        """
        # 获取临时变量实例
        cache_vars = VariableCache()

        # 获取所有环境变量
        try:
            env = target['config']['request']['env']
        except KeyError:
            raise ValueError('测试环境获取失败, 测试用例数据缺少 config:request:env 参数')
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

        while re.findall(self.vars_re, str_target):
            key = re.search(self.vars_re, str_target)
            var_key = key.group(1) or key.group(2)

            # 替换: 临时变量 > 环境变量 > 全局变量
            if var_key is not None:
                value = cache_vars.get(var_key)
                if value is None:
                    try:
                        value = str(env_vars[f'{var_key}'])
                        str_target = re.sub(self.vars_re, value, str_target, 1)
                    except KeyError:
                        value = str(read_vars[f'{var_key}'])
                        str_target = re.sub(self.vars_re, value, str_target, 1)
                    except Exception as e:
                        log.error('请求数据变量"{}"替换失败: {}'.format(var_key, e))
                        raise e

        if isinstance(str_target, str):
            str_target = eval(str_target)

        return str_target

    @staticmethod
    def teardown_var_extract(response: dict, extract: list, env=None):
        """
        后置参数提取

        :param response:
        :param extract:
        :param env:
        :return:
        """
        for et in extract:
            key = et['key']
            set_type = et['set_type']
            json_path = et['jsonpath']
            value = jsonpath(response, json_path)
            if value:
                value = value[0]
            else:
                raise ValueError(f'jsonpath取值失败, 表达式: {json_path}')
            if set_type is None:
                VariableCache().set(key, value)
            elif set_type == 'cache':
                VariableCache().set(key, value)
            elif set_type == 'env':
                write_env_vars(RUN_ENV_PATH, env, key, value)
            elif set_type == 'global':
                write_yaml_vars({key: value})
            else:
                raise ValueError('前置 sql 设置变量失败, 用例参数 "set_type" 类型错误')
