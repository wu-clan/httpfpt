#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os.path
import re

from jsonpath import findall

from httpfpt.common.env_handler import get_env_dict, write_env_vars
from httpfpt.common.errors import JsonPathFindError, RequestDataParseError, VariableError
from httpfpt.common.log import log
from httpfpt.common.variable_cache import variable_cache
from httpfpt.common.yaml_handler import read_yaml, write_yaml_vars
from httpfpt.core.path_conf import RUN_ENV_PATH, TEST_DATA_PATH
from httpfpt.enums.var_type import VarType


class VarsExtractor:
    def __init__(self) -> None:
        # 变量通用规则：
        # 1. 开头必须为 a-zA-Z_
        # 2. 变量有 {} 包住时，允许变量值前后存在任何内容，相反，则不允许变量值前后存在任何内容
        # 变量表达: ${var} 或 $var
        self.vars_re = re.compile(r'\${([a-zA-Z_]\w*)}|(?<!\S)\$([a-zA-Z_]\w*)(?!\S)')
        # 关联变量表达: ^{var} 或 ^var
        self.relate_vars_re = re.compile(r'\^{([a-zA-Z_]\w*)}|(?<!\S)\^([a-zA-Z_]\w*)(?!\S)')
        # SQL 变量语法: :{var} 或 :var
        self.sql_vars_re = re.compile(r':{([a-zA-Z_]\w*)}|(?<!\S):([a-zA-Z_]\w*)(?!\S)')

    def vars_replace(self, target: dict, env_filename: str | None = None) -> dict:
        """
        变量替换

        :param target:
        :param env_filename:
        :return:
        """
        str_target = json.dumps(target, ensure_ascii=False)

        match = self.vars_re.search(str_target) or self.sql_vars_re.search(str_target)
        if not match:
            return target

        # 获取环境名称
        env = env_filename or target.get('config', {}).get('request', {}).get('env')
        if not env or not isinstance(env, str):
            raise RequestDataParseError('运行环境获取失败, 测试用例数据缺少 config:request:env 参数')
        try:
            env_file = os.path.join(RUN_ENV_PATH, env)
            env_vars = get_env_dict(env_file)
        except OSError:
            raise RequestDataParseError('运行环境获取失败, 请检查测试用例环境配置')

        # 获取全局变量
        global_vars = read_yaml(TEST_DATA_PATH, filename='global_vars.yaml')

        # 获取 re 规则字符串
        var_re = self.sql_vars_re if env_filename else self.vars_re
        for match in var_re.finditer(str_target):
            var_key = match.group(1) or match.group(2)
            if var_key is not None:
                log_type = '请求数据'
                try:
                    # 设置默认值为特殊字符, 避免变量值为 None 时错误判断
                    default = '`AE86`'
                    # 替换: 临时变量 > 环境变量 > 全局变量
                    cache_value = variable_cache.get(var_key, default=default)
                    if cache_value == default:
                        var_value = env_vars.get(var_key.upper(), global_vars.get(var_key, default))
                        if var_value != default:
                            if env_filename is not None:
                                log_type = 'SQL '
                            str_target = var_re.sub(str(var_value), str_target, 1)
                            log.info(f'{log_type}变量 {var_key} 替换完成')
                        else:
                            raise VariableError(var_key)
                    else:
                        str_target = var_re.sub(str(cache_value), str_target, 1)
                        log.info(f'{log_type}变量 {var_key} 替换完成')
                except Exception as e:
                    raise VariableError(f'{log_type}变量 {var_key} 替换失败: {e}')

        dict_target = json.loads(str_target)

        return dict_target

    def relate_vars_replace(self, target: dict) -> dict:
        """
        关联变量替换

        :param target:
        :return:
        """
        str_target = json.dumps(target, ensure_ascii=False)

        match = self.relate_vars_re.search(str_target)
        if not match:
            return target

        var_keys = []
        log.info('执行关联测试用例变量替换...')
        for match in self.relate_vars_re.finditer(str_target):
            var_key = match.group(1) or match.group(2)
            if var_key is not None:
                var_keys.append(var_key)
                default = '`AE86`'
                cache_value = variable_cache.get(var_key, default=default, tag='relate_testcase')
                if cache_value != default:
                    try:
                        str_target = self.relate_vars_re.sub(str(cache_value), str_target, 1)
                        log.info(f'请求数据关联变量 {var_key} 替换完成')
                    except Exception as e:
                        raise VariableError(f'请求数据关联变量 {var_key} 替换失败: {e}')
                else:
                    raise VariableError(f'请求数据关联变量替换失败，临时变量池不存在变量: "{var_key}"')

        log.info('关联测试用例变量替换完毕')
        # TODO: https://github.com/StKali/cache3/issues/18
        if var_keys:
            log.info('自动清理关联变量中...')
            for var_key in var_keys:
                variable_cache.delete(var_key, tag='relate_testcase')

        dict_target = json.loads(str_target)

        return dict_target

    @staticmethod
    def teardown_var_extract(response: dict, extract: dict, env: str) -> None:
        """
        后置参数提取

        :param response:
        :param extract:
        :param env:
        :return:
        """
        log.info(f'执行变量提取：{extract["key"]}')

        key = extract['key']
        set_type = extract['type']
        json_path = extract['jsonpath']
        value = findall(json_path, response)
        if not value:
            raise JsonPathFindError(f'jsonpath 取值失败, 表达式: {json_path}')
        value_str = str(value[0])
        if set_type == VarType.CACHE:
            variable_cache.set(key, value_str)
        elif set_type == VarType.ENV:
            write_env_vars(RUN_ENV_PATH, env, key, value_str)
        elif set_type == VarType.GLOBAL:
            write_yaml_vars({key: value_str})
        else:
            raise VariableError(
                f'前置 SQL 设置变量失败, 用例参数 "type: {set_type}" 值错误, 请使用 cache / env / global'
            )


var_extractor = VarsExtractor()
