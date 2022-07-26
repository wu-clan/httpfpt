#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class AssertType:
    # 是否相等
    equal = "eq"
    # 判断实际结果不等于预期结果
    not_equal = "not_eq"
    # 判断实际结果大于预期结果
    greater_than = "gt"
    # 判断实际结果大于等于预期结果
    greater_than_or_equal = "ge"
    # 判断实际结果小于预期结果
    less_than = "lt"
    # 判断实际结果小于等于预期结果
    less_than_or_equal = "le"
    # 判断字符串是否相等
    string_equal = "str_eq"
    # 判断长度等于
    length_equal = "len_eq"
    # 判断长度不相等
    not_length_equal = "not_len_eq"
    # 判断长度小于
    length_less_than = "len_lt"
    # 判断长度小于等于
    length_less_than_or_equal = 'len_le'
    # 判断长度大于
    length_greater_than = "len_gt"
    # 判断长度大于等于
    length_greater_than_or_equal = 'len_ge'
    # 判断期望结果内容包含在实际结果中
    contains = "contains"
    # 判断实际结果包含在期望结果中
    not_contains = 'not contains'
    # 检查响应内容的开头是否和预期结果内容的开头相等
    startswith = 'startswith'
    # 检查响应内容的结尾是否和预期结果内容相等
    endswith = 'endswith'
