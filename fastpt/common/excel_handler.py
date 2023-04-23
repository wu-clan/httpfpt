#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from typing import Any, Dict, List, Optional

import xlrd

from fastpt.common.log import log


def read_excel(filepath: str, *, filename: str, sheet: str = 'Sheet1') -> List[Dict[str, Optional[Any]]]:
    """
    读取 xlsx 文件

    :param filepath: 文件路径
    :param filename: 文件名
    :param sheet: 工作表
    :return:
    """
    file = os.path.join(filepath, filename)
    data = xlrd.open_workbook(file)
    table = data.sheet_by_name(sheet)
    # 获取总行,列数
    rows = table.nrows
    cols = table.ncols  # noqa F841
    if rows > 1:
        # 获取第一行内容, 通常为列说明
        keys = table.row_values(0)
        data_list = []
        # 获取文档剩下所有内容
        for col in range(1, rows):
            values = table.row_values(col)
            # key, value组合为字典
            data = dict(zip(keys, values))
            # 数据整理
            for value in data:
                # 替换空字符串为 None, 保证与 yaml 数据返回格式一致
                if data[value] == '':
                    data[value] = None
            data_list.append(data)
        return data_list
    else:
        log.warning(f'数据表格 {filename} 没有数据!')
        raise ValueError(f'数据表格 {filename} 没有数据! 请检查数据文件内容是否正确!')
