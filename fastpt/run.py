#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import os
import shutil
from typing import Union, Optional

import pytest

from fastpt.core.get_conf import PROJECT_NAME
from fastpt.core.path_conf import HTML_REPORT_PATH, ALLURE_REPORT_PATH, ALLURE_ENV_FILE, ALLURE_REPORT_ENV_FILE
from fastpt.utils.send_email import SendMail


def run(
        *args,
        log_level: str = '-v',
        # cases path
        class_path: Optional[str] = None,
        function_path: Optional[str] = None,
        # html report
        html_report: bool = True,
        send_report: bool = False,
        # allure
        allure: bool = True,
        clear_allure: bool = True,
        allure_serve: bool = True,
        # extra
        reruns: int = 0,
        maxfail: int = 0,
        x: bool = False,
        n: Union[str, int] = 'auto',
        dist: str = 'loadscope',
        markers: bool = True,
        captrue: bool = True,
        disable_warings: bool = True,
        **kwargs,
):
    """
    运行入口

    :param log_level: 控制台打印输出级别, 默认"-v"
    :param class_path: 可选参数, 指定测试用例类, 默认为空
    :param function_path: 可选参数, 指定测试用例函数, 默认为空
    :param html_report: 是否生成 HTML 测试报告, 默认开启
    :param send_report: 是否发送测试报告, 默认发送, 如果已启用生成 html 测试报告
    :param allure: allure 测试报告, 默认开启
    :param clear_allure: 清空 allure 报告历史记录, 默认开启
    :param allure_serve: 是否测试执行完成后自动打开 allure 测试报告服务, 如果已启用 allure 测试报告
    :param reruns: 每个用例的运行次数, 兼容性差, 默认关闭, 不建议开启
    :param maxfail: 大于0的正整数, 指定失败用例个数,到达数量上限后终止运行, 默认为0, 为0时表示此参数默认关闭
    :param x: 如果发生失败用例, 是否终止运行, 默认关闭
    :param n: 分布式运行,使用"auto"表示全核, 也可指定cpu内核数量, 大于0的正整数, 默认"auto"
    :param dist: 分布式顺序运行方式, 默认"loadscope", 详情:https://pytest-xdist.readthedocs.io/en/latest/distribution.html#
    :param markers: markers 严格模式,只允许使用用例中创建的 mark,并只运行 pytest.ini 中 markers 包含的 mark 用例, 默认开启
    :param captrue: 避免在使用输出模式为"v"和"s"时,html报告中的表格log为空的情况, 默认开启
    :param disable_warings: 是否关闭控制台警告信息, 默认开启
    :return:
    """
    case_path = f"./testcase/{PROJECT_NAME}"  # 默认执行指定项目下的所有测试用例
    if class_path is None and function_path is None:
        run_path = case_path
    elif class_path is not None and function_path is None:
        if '::' not in class_path:
            raise ValueError(
                '类用例收集失败, 请检查路径参数 \n'
                'example: \n'
                '\tclass_path = "文件名::类名"'
            )
        run_path = case_path + '/' + class_path
    elif function_path is not None and class_path is None:
        if '::' not in function_path:
            raise ValueError(
                '类用例收集失败, 请检查路径参数 \n'
                'example: \n'
                '\t1. function_path = "文件名::类名::函数名" \n'
                '\t2. function_path = "文件名::函数名"'
            )
        run_path = case_path + '/' + function_path
    else:
        raise ValueError(
            '获取测试用例失败, 请检查路径运行参数, 参数 class_path 和 function_path 只能使用其中一种指定方式,'
            '并将另一种方式设置为None, 否则引发此异常'
        )

    if html_report:
        if not os.path.exists(HTML_REPORT_PATH):
            os.makedirs(HTML_REPORT_PATH)

    is_html_report_file = f'''--html={HTML_REPORT_PATH}\\{PROJECT_NAME}_{datetime.datetime.now().strftime(
        "%Y-%m-%d %H_%M_%S")}.html''' if html_report else ''

    is_html_report_self = '--self-contained-html' if html_report else ''

    is_allure = f'--alluredir={ALLURE_REPORT_PATH}' if allure else ''

    is_clear_allure = f'--clean-alluredir' if is_allure and clear_allure else ''

    is_reruns = f'--reruns {reruns}' if reruns != 0 else ''

    is_maxfail = f'--maxfail={maxfail}' if maxfail != 0 else ''

    is_x = '-x' if x else ''

    is_n = f'-n={n}'

    is_dist = f'--dist={dist}'

    is_markers = '--strict-markers' if markers else ''

    is_captrue = '--capture=tee-sys' if captrue else ''

    is_disable_warings = '--disable-warnings' if disable_warings else ''

    kw = [f"'{k}={v}'" for k, v in kwargs.items()]

    pytest.main(
        [
            *args,
            f'{log_level}',
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
        ] + kw
    )

    SendMail(is_html_report_file.split('=')[1]).send() if send_report else ... if html_report else ...

    shutil.copyfile(ALLURE_ENV_FILE, ALLURE_REPORT_ENV_FILE) if allure else ...
    os.popen(f'allure serve {ALLURE_REPORT_PATH}') if allure_serve else ... if allure else ...


if __name__ == '__main__':
    run()
