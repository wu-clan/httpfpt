#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime


def get_current_time() -> str:
    """
    获取当前时间

    :return:
    """
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
