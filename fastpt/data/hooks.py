#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
from faker import Faker

fk = Faker(locale='zh_CN')


def current_time():
    """
    :return: 获取当前时间
    """
    return datetime.datetime.now()


def random_phone():
    """
    :return: 随机手机号
    """
    return fk.phone_number()


def sum_a_b(a, b):
    return a + b
