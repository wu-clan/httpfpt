#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re


def get_file_property(filepath: str) -> tuple:
    """
    获取文件属性

    :param filepath:
    :return:
    """
    filename = re.split(r'/|\'|\\|\\\\', filepath)[-1]
    file_real_name = '.'.join(filename.split('.')[:-1])
    filetype = filename.split('.')[-1]
    return filename, file_real_name, filetype
