#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
from typing import Union, Optional

import pytest

from fastpt.core.get_conf import PROJECT_NAME
from fastpt.core.path_conf import HTML_REPORT_PATH


def run():
    """
    PS: 运行参数配置
        - print_level:      str, 控制台打印输出级别
        - project_path:     str, 可选参数, 指定测试用例项目路径
        - class_path:       str, 可选参数, 指定测试用例类
        - function_path:    str, 可选参数, 指定测试用例函数
        - html_report:      bool, 是否生成HTML测试报告
        - reruns:           int, 每个用例的运行次数, 兼容性差, 此插件默认关闭
        - maxfail:          int, 大于0的正整数, 指定失败用例个数,到达数量上限后终止运行
        - x:                bool, 如果发生失败用例,是否终止运行
        - n:                str/int, 分布式运行,使用"auto"表示全核或指定cpu内核数量
        - dist:             str, 分布式顺序运行方式, 详情:https://pytest-xdist.readthedocs.io/en/latest/distribution.html#
        - markers           bool, markers严格模式,只允许使用用例中创建的mark,并只运行pytest.ini中markers包含的mark用例
        - captrue           bool, 避免在使用输出模式为"v"和"s"时,html报告中的表格log为空的情况
        - disable_warings:  bool, 是否关闭控制台警告信息
    """

    # -------------------------- args setting -----------------------------

    print_level: str = '-v'
    project_path: Optional[str] = f"./testcase/{PROJECT_NAME}/"
    class_path: Optional[str] = None
    function_path: Optional[str] = None
    html_report: bool = True
    reruns: int = 0
    maxfail: int = 0
    x: bool = False
    n: Union[str, int] = 'auto'
    dist: str = 'loadscope'
    markers: str = '--strict-markers'
    captrue: str = '--capture=tee-sys'
    disable_warings: bool = True

    # ---------------------------------------------------------------------

    # 获取指定的测试用例
    if project_path is not None and class_path is None and function_path is None:
        run_path = project_path
    elif class_path is not None and project_path is None and function_path is None:
        run_path = class_path
    elif function_path is not None and project_path is None and class_path is None:
        run_path = function_path
    else:
        raise ValueError(
            '获取测试用例失败,请检查用例参数 \n\n'
            'example: \n'
            '\t__project = f"./testcase/{PROJECT_NAME}/" \n'
            '\t__class = f"./testcase/{PROJECT_NAME}//文件名::类名" \n'
            '\t__function = f"./testcase/{PROJECT_NAME}//文件名::类名::函数名" or __function = f"./testcase/{PROJECT_NAME}//文件名::函数名" \n\n'
            '你只能指定三种方式中的其中一种,并将另外两种方式设置为None,否则引发此异常'
        )

    # --html
    if html_report:
        if not os.path.exists(HTML_REPORT_PATH):
            os.makedirs(HTML_REPORT_PATH)
        is_html_report_file = f'--html={HTML_REPORT_PATH}\\{PROJECT_NAME}_{time.strftime("%Y-%m-%d %H_%M_%S")}.html'
        is_html_report_self = '--self-contained-html'
    else:
        is_html_report_file = ''
        is_html_report_self = ''

    # --reruns
    if reruns != 0:
        is_reruns = f'--reruns {reruns}'
    else:
        is_reruns = ''

    # --maxfail
    if maxfail != 0:
        is_maxfail = f'--maxfail={maxfail}'
    else:
        is_maxfail = ''

    # -x
    if x:
        is_x = '-x'
    else:
        is_x = ''

    # -n
    is_n = f'-n={n}'

    # --dist
    is_dist = f'--dist={dist}'

    # --disable-warnings
    if disable_warings:
        is_disable_warings = '--disable-warnings'
    else:
        is_disable_warings = ''

    pytest.main([
        f'{print_level}',
        f'{run_path}',
        f'{is_html_report_file}',
        f'{is_html_report_self}',
        # f'{is_reruns}'
        f'{is_maxfail}',
        f'{is_x}',
        f'{is_n}',
        f'{is_dist}',
        f'{is_disable_warings}',
        f'{markers}',
        f'{captrue}'
    ])


if __name__ == '__main__':
    run()
