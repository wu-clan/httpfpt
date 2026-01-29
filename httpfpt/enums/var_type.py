from enum import unique

from httpfpt.enums import StrEnum


@unique
class VarType(StrEnum):
    CACHE = 'cache'
    ENV = 'env'
    GLOBAL = 'global'
