from __future__ import annotations

import json
import os.path
import re

from httpfpt.common.env_handler import get_env_dict
from httpfpt.common.errors import RequestDataParseError, VariableError
from httpfpt.common.log import log
from httpfpt.common.variable_cache import variable_cache
from httpfpt.common.yaml_handler import read_yaml
from httpfpt.core.path_conf import httpfpt_path
from httpfpt.utils.request.vars_recorder import record_variables


class VarsExtractor:
    def __init__(self) -> None:
        # 变量通用规则：
        # 1. 开头必须为 a-zA-Z_
        # 2. 变量有 {} 包住时，允许变量值前后存在任何内容，相反，则不允许变量值前后存在任何内容
        # 变量表达: ${var} 或 $var
        self.vars_re = re.compile(r'\${([a-zA-Z_]\w*)}|(?<!\S)\$([a-zA-Z_]\w*)(?!\S)')
        # 关联变量表达: ^{var} 或 ^var
        self.relate_vars_re = re.compile(r'\^{([a-zA-Z_]\w*)}|(?<!\S)\^([a-zA-Z_]\w*)(?!\S)')

    def vars_replace(self, target: str | dict, env: str) -> str | dict:
        """
        变量替换

        :param target:
        :param env:
        :return:
        """
        if isinstance(target, dict):
            str_target = json.dumps(target, ensure_ascii=False)
        else:
            str_target = target

        match = self.vars_re.search(str_target)
        if not match:
            return target

        # 获取环境名称
        if not env or not isinstance(env, str):
            raise RequestDataParseError('运行环境获取失败, 测试用例数据缺少 config:request:env 参数')

        try:
            env_file = os.path.join(httpfpt_path.run_env_dir, env)
            env_vars = get_env_dict(env_file)
        except OSError:
            raise RequestDataParseError('运行环境获取失败, 请检查测试用例环境配置')

        for match in self.vars_re.finditer(str_target):
            var_key = match.group(1) or match.group(2)
            if var_key is not None:
                try:
                    cache_value = variable_cache.get(var_key)
                    if cache_value is None:
                        global_vars = read_yaml(httpfpt_path.global_var_dir, filename='global_vars.yaml')
                        var_value = env_vars.get(
                            var_key.upper(), global_vars.get(var_key) if global_vars is not None else None
                        )
                        if var_value is None:
                            raise VariableError(var_key)
                        log.info(f'变量 {var_key}={var_value} 替换完成')
                        str_target = self.vars_re.sub(str(var_value), str_target, 1)
                    else:
                        log.info(f'变量 {var_key}={cache_value} 替换完成')
                        str_target = self.vars_re.sub(str(cache_value), str_target, 1)
                except Exception as e:
                    raise VariableError(f'变量 {var_key} 替换失败: {e}')

        if isinstance(target, dict):
            return json.loads(str_target)

        return str_target

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
                        log.info(f'用例数据关联变量 {var_key} 替换完成')
                    except Exception as e:
                        raise VariableError(f'用例数据关联变量 {var_key} 替换失败: {e}')
                else:
                    raise VariableError(f'用例数据关联变量替换失败，临时变量池不存在变量: "{var_key}"')

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
        record_variables(json_path, response, key, set_type, env)


var_extractor = VarsExtractor()
