#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os.path
import re

from jsonpath import jsonpath

from httpfpt.common.env_handler import get_env_dict, write_env_vars
from httpfpt.common.log import log
from httpfpt.common.variable_cache import VariableCache
from httpfpt.common.yaml_handler import read_yaml, write_yaml_vars
from httpfpt.core.path_conf import TEST_DATA_PATH, RUN_ENV_PATH
from httpfpt.enums.var_type import VarType


class VarsExtractor:
    def __init__(self) -> None:
        # 变量表达: ${var} 或 $var
        # 变量开头: a-zA-Z_
        self.vars_re = r'\$([a-zA-Z_]\w*)|\${([a-zA-Z_]\w*)\}'
        # 关联变量表达: ^{var} 或 ^var
        # 关联变量开头: a-zA-Z_
        self.relate_vars_re = r'\^([a-zA-Z_]\w*)|\^{([a-zA-Z_]\w*)\}'

    def vars_replace(self, target: dict) -> dict:
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
        str_target = str(target)

        while re.findall(self.vars_re, str_target):
            key = re.search(self.vars_re, str_target)
            var_key = key.group(1) or key.group(2)

            # 替换: 临时变量 > 环境变量 > 全局变量
            if var_key is not None:
                value = str(cache_vars.get(var_key))
                if value is None:
                    try:
                        value = str(env_vars[f'{var_key}'])
                        str_target = re.sub(self.vars_re, value, str_target, 1)
                        log.info(f'请求数据变量 {var_key} 替换完成')
                    except KeyError:
                        value = str(read_vars[f'{var_key}'])
                        str_target = re.sub(self.vars_re, value, str_target, 1)
                        log.info(f'请求数据变量 {var_key} 替换完成')
                    except Exception as e:
                        log.error(f'请求数据变量 {var_key} 替换失败: {e}')
                        raise e
                else:
                    str_target = re.sub(self.vars_re, value, str_target, 1)

        dict_target = eval(str_target)

        return dict_target

    def relate_vars_replace(self, target: dict) -> dict:
        """
        关联变量替换

        :param target:
        :return:
        """
        # 获取临时变量实例
        cache_vars = VariableCache()

        # 获取变量
        str_target = str(target)

        while re.findall(self.relate_vars_re, str_target):
            key = re.search(self.relate_vars_re, str_target)
            var_key = key.group(1) or key.group(2)

            if var_key is not None:
                value = str(cache_vars.get(var_key))
                if value is None:
                    err_msg = '请求数据关联变量替换失败，临时变量池不存在变量: “{}”'.format(var_key)
                    log.error(err_msg)
                    raise ValueError(err_msg)
                else:
                    try:
                        str_target = re.sub(self.relate_vars_re, value, str_target, 1)
                        log.info(f'请求数据关联变量 {var_key} 替换完成')
                    except Exception as e:
                        log.error(f'请求数据关联变量 {var_key} 替换失败: {e}')
                        raise e

            # 删除关联用例临时变量
            VariableCache().delete(var_key)

        dict_target = eval(str_target)

        return dict_target

    @staticmethod
    def teardown_var_extract(response: dict, extract: list, env: str) -> None:
        """
        后置参数提取

        :param response:
        :param extract:
        :param env:
        :return:
        """
        for et in extract:
            log.info(f'执行变量提取：{et["key"]}')
            key = et['key']
            set_type = et['type']
            json_path = et['jsonpath']
            value = jsonpath(response, json_path)
            if value:
                value = value[0]
            else:
                raise ValueError(f'jsonpath 取值失败, 表达式: {json_path}')
            if set_type == VarType.CACHE:
                VariableCache().set(key, value)
            elif set_type == VarType.ENV:
                write_env_vars(RUN_ENV_PATH, env, key, value)
            elif set_type == VarType.GLOBAL:
                write_yaml_vars({key: value})
            else:
                raise ValueError(f'前置 sql 设置变量失败, 用例参数 "type: {set_type}" 值错误, 请使用 cache / env / global')  # noqa: E501
