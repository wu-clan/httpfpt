#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import operator

from faker import Faker

faker = Faker(locale='zh_CN')


def current_time() -> datetime.datetime:
    """
    :return: 获取当前时间
    """
    return datetime.datetime.now()


def random_phone() -> str:
    """
    :return: 随机手机号
    """
    return faker.phone_number()


def sum_a_b(a: int, b: int) -> int:
    return operator.add(a, b)
