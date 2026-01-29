from jsonpath import findall

from httpfpt.common.env_handler import write_env_vars
from httpfpt.common.errors import JsonPathFindError, VariableError
from httpfpt.common.variable_cache import variable_cache
from httpfpt.common.yaml_handler import write_yaml_vars
from httpfpt.core.path_conf import httpfpt_path
from httpfpt.enums.var_type import VarType


def record_variables(jsonpath: str, target: dict, key: str, set_type: str, env: str) -> None:
    """
    记录变量

    :param jsonpath:
    :param set_type:
    :param target:
    :param key:
    :param env:
    :return:
    """
    value = findall(jsonpath, target)
    if not value:
        raise JsonPathFindError(f'jsonpath 取值失败, 表达式: {jsonpath}')
    value_str = str(value[0])
    if set_type == VarType.CACHE:
        variable_cache.set(key, value_str)
    elif set_type == VarType.ENV:
        write_env_vars(httpfpt_path.run_env_dir, env, key, value_str)
    elif set_type == VarType.GLOBAL:
        write_yaml_vars({key: value_str})
    else:
        raise VariableError(f'变量设置失败, 用例参数 "type: {set_type}" 值错误, 请使用 cache / env / global')
