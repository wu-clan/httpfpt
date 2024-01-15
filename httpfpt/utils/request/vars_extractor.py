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
        # 变量表达: ${var} 或 $var
        # 变量开头: a-zA-Z_
        self.vars_re = r'\$([a-zA-Z_]\w*)|\${([a-zA-Z_]\w*)\}'
        # 关联变量表达: ^{var} 或 ^var
        # 关联变量开头: a-zA-Z_
        self.relate_vars_re = r'\^([a-zA-Z_]\w*)|\^{([a-zA-Z_]\w*)\}'

    def vars_replace(self, target: dict, env_filename: str | None = None) -> dict:
        """
        变量替换

        :param target:
        :param env_filename:
        :return:
        """
        str_target = json.dumps(target, ensure_ascii=False)

        # 获取变量名
        key = re.search(self.vars_re, str_target)
        var_key = key.group(1) or key.group(2)
        if var_key is None:
            dict_target = json.loads(str_target)
            return dict_target

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

        while re.findall(self.vars_re, str_target):
            # 替换: 临时变量 > 环境变量 > 全局变量
            if var_key is not None:
                log_type = '请求数据'
                try:
                    cache_value = variable_cache.get(var_key)
                    if cache_value is None:
                        value = env_vars.get(var_key.upper()) or global_vars.get(var_key)
                        if value is not None:
                            if env_filename is not None:
                                log_type = 'SQL '
                            str_target = re.sub(self.vars_re, str(value), str_target, 1)
                            log.info(f'{log_type}变量 {var_key} 替换完成')
                        else:
                            raise VariableError(var_key)
                    else:
                        str_target = re.sub(self.vars_re, str(cache_value), str_target, 1)
                        log.info(f'{log_type}变量 {var_key} 替换完成')
                except Exception as e:
                    log_err_msg = f'{log_type}变量 {var_key} 替换失败'
                    log.error(log_err_msg)
                    raise VariableError(f'{log_err_msg}: {e}')

        dict_target = json.loads(str_target)

        return dict_target

    def relate_vars_replace(self, target: dict) -> dict:
        """
        关联变量替换

        :param target:
        :return:
        """
        str_target = json.dumps(target)

        while re.findall(self.relate_vars_re, str_target):
            key = re.search(self.relate_vars_re, str_target)
            var_key = key.group(1) or key.group(2)

            if var_key is not None:
                cache_value = str(variable_cache.get(var_key))
                if cache_value == 'None':
                    err_msg = '请求数据关联变量替换失败，临时变量池不存在变量: “{}”'.format(var_key)
                    log.error(err_msg)
                    raise VariableError(err_msg)
                else:
                    try:
                        str_target = re.sub(self.relate_vars_re, cache_value, str_target, 1)
                        log.info(f'请求数据关联变量 {var_key} 替换完成')
                    except Exception as e:
                        log.error(f'请求数据关联变量 {var_key} 替换失败: {e}')
                        raise VariableError(f'请求数据关联变量 {var_key} 替换失败: {e}')

            # 删除关联用例临时变量
            variable_cache.delete(var_key)

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
        if value:
            value = str(value[0])
        else:
            raise JsonPathFindError(f'jsonpath 取值失败, 表达式: {json_path}')
        if set_type == VarType.CACHE:
            variable_cache.set(key, value)
        elif set_type == VarType.ENV:
            write_env_vars(RUN_ENV_PATH, env, key, value)
        elif set_type == VarType.GLOBAL:
            write_yaml_vars({key: value})
        else:
            raise VariableError(
                f'前置 sql 设置变量失败, 用例参数 "type: {set_type}" 值错误, 请使用 cache / env / global'
            )


var_extractor = VarsExtractor()
