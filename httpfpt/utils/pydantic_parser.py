from pydantic import ValidationError

from httpfpt.common.log import log


def parse_error(error: ValidationError) -> int:
    """
    解析 pydantic 验证错误

    :param error:
    :return:
    """
    error_count = error.error_count()
    error_str = str(error)
    log.error(error_str)
    return error_count
