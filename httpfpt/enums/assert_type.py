from enum import unique

from httpfpt.enums import StrEnum


@unique
class AssertType(StrEnum):
    equal = 'eq'
    not_equal = 'not_eq'
    greater_than = 'gt'
    greater_than_or_equal = 'ge'
    less_than = 'lt'
    less_than_or_equal = 'le'
    string_equal = 'str_eq'
    length_equal = 'len_eq'
    not_length_equal = 'not_len_eq'
    length_less_than = 'len_lt'
    length_less_than_or_equal = 'len_le'
    length_greater_than = 'len_gt'
    length_greater_than_or_equal = 'len_ge'
    contains = 'contains'
    not_contains = 'not_contains'
    startswith = 'startswith'  # type: ignore
    endswith = 'endswith'  # type: ignore
