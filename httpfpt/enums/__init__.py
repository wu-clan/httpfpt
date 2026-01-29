from enum import Enum


class IntEnum(int, Enum):
    """整型枚举"""

    pass


class StrEnum(str, Enum):
    """字符串枚举"""

    pass
