from enum import unique

from httpfpt.enums import StrEnum


@unique
class SqlType(StrEnum):
    select = 'SELECT'
    insert = 'INSERT'
    update = 'UPDATE'
    delete = 'DELETE'
