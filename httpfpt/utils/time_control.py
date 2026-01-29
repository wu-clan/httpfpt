import datetime


def get_current_time(strf: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    获取当前时间

    :param strf:
    :return:
    """
    return datetime.datetime.now().strftime(strf)


def get_current_timestamp() -> str:
    """获取当前时间戳"""
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f')
