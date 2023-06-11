#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime


def get_current_time() -> str:
    """
    :return: 当前时间
    """
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_current_timestamp() -> str:
    """
    :return: 当前时间戳
    """
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f')
