from enum import unique

from httpfpt.enums import StrEnum


@unique
class MethodType(StrEnum):
    get = 'GET'
    post = 'POST'
    put = 'PUT'
    delete = 'DELETE'
    patch = 'PATCH'
