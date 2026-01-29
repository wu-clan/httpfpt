from __future__ import annotations

from httpfpt.common.errors import RequestDataParseError


def get_ids(request_data: dict | list) -> list:
    """
    从请求数据获取数据驱动下的 ids 数据

    :param request_data: 请求数据
    :return:
    """
    ids = []
    try:
        if isinstance(request_data, dict):
            module = request_data['config']['module']
            name = request_data['test_steps']['name']
            case_id = request_data['test_steps']['case_id']
            ids.append(f'module: {module}, name: {name}, case_id: {case_id}')
        else:
            for data in request_data:
                module = data['config']['module']
                name = data['test_steps']['name']
                case_id = data['test_steps']['case_id']
                ids.append(f'module: {module}, name: {name}, case_id: {case_id}')
    except KeyError as e:
        raise RequestDataParseError('测试用例 ids 获取失败, 请检查测试用例数据是否符合规范: {}'.format(e))
    return ids
