#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
from typing import Union, Optional

import pytest

from fastpt.core.get_conf import PROJECT_NAME
from fastpt.core.path_conf import HTML_REPORT_PATH, ALLURE_REPORT_PATH
from fastpt.utils.send_email import SendMail


def run():
    """
    PS: 运行参数配置
        - print_level:      str, 控制台打印输出级别, 默认"-v"
        - project_path:     str, 可选参数, 指定测试用例项目路径, 默认"./testcase/{PROJECT_NAME}/"
        - class_path:       str, 可选参数, 指定测试用例类, 默认为空
        - function_path:    str, 可选参数, 指定测试用例函数, 默认为空
        - html_report:      bool, 是否生成HTML测试报告, 默认开启
        - allure:           bool, allure测试报告, 默认开启
        - clear_allure:     bool, 清空allure报告历史记录, 默认开启
        - reruns:           int, 每个用例的运行次数, 兼容性差, 默认关闭
        - maxfail:          int, 大于0的正整数, 指定失败用例个数,到达数量上限后终止运行, 默认为0, 为0时表示此参数默认关闭
        - x:                bool, 如果发生失败用例,是否终止运行, 默认关闭
        - n:                str/int, 分布式运行,使用"auto"表示全核, 也可指定cpu内核数量, 大于0的正整数, 默认"auto"
        - dist:             str, 分布式顺序运行方式, 默认"loadscope", 详情:https://pytest-xdist.readthedocs.io/en/latest/distribution.html#
        - markers           bool, markers严格模式,只允许使用用例中创建的mark,并只运行pytest.ini中markers包含的mark用例, 默认开启
        - captrue           bool, 避免在使用输出模式为"v"和"s"时,html报告中的表格log为空的情况, 默认开启
        - disable_warings:  bool, 是否关闭控制台警告信息, 默认开启
    """

    # -------------------------- args settings -----------------------------

    print_level: str = '-v'
    project_path: Optional[str] = f"./testcase/{PROJECT_NAME}/"
    class_path: Optional[str] = None
    function_path: Optional[str] = None
    html_report: bool = True
    allure: bool = True
    clear_allure: bool = True
    reruns: int = 0
    maxfail: int = 0
    x: bool = False
    n: Union[str, int] = 'auto'
    dist: str = 'loadscope'
    markers: bool = True
    captrue: bool = True
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

    # --alluredir
    if allure:
        is_allure = f'--alluredir={ALLURE_REPORT_PATH}'
    else:
        is_allure = ''

    # --clean-alluredir
    if clear_allure:
        is_clear_allure = f'--clean-alluredir'
    else:
        is_clear_allure = ''

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

    # --markers
    if markers:
        is_markers = '--strict-markers'
    else:
        is_markers = ''

    # --captrue
    if captrue:
        is_captrue = '--capture=tee-sys'
    else:
        is_captrue = ''

    # --disable-warnings
    if disable_warings:
        is_disable_warings = '--disable-warnings'
    else:
        is_disable_warings = ''

    # 运行入口
    pytest.main([
        f'{print_level}',
        f'{run_path}',
        f'{is_html_report_file}',
        f'{is_html_report_self}',
        f'{is_allure}',
        f'{is_clear_allure}'
        # f'{is_reruns}'
        f'{is_maxfail}',
        f'{is_x}',
        f'{is_n}',
        f'{is_dist}',
        f'{is_markers}',
        f'{is_captrue}',
        f'{is_disable_warings}'
    ])

    # 发送测试报告
    if html_report:
        send_mail = SendMail("--html=q".split('=')[1])
        send_mail.send()


if __name__ == '__main__':
    run()
