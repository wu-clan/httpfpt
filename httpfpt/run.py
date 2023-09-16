#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import os
import shutil
from typing import Union, Optional, Literal

import pytest

from httpfpt.common.log import log
from httpfpt.common.yaml_handler import read_yaml
from httpfpt.core.get_conf import PROJECT_NAME, EMAIL_REPORT_SEND, DING_TALK_REPORT_SEND, LARK_TALK_REPORT_SEND
from httpfpt.core.path_conf import (
    HTML_REPORT_PATH,
    ALLURE_REPORT_PATH,
    ALLURE_ENV_FILE,
    ALLURE_REPORT_ENV_FILE,
    ALLURE_REPORT_HTML_PATH,
    YAML_REPORT_PATH,
)
from httpfpt.db.redis_db import redis_client
from httpfpt.utils.request import case_data_parse as case_data
from httpfpt.utils.send_report.ding_talk import DingTalk
from httpfpt.utils.send_report.lark_talk import LarkTalk
from httpfpt.utils.send_report.send_email import SendMail


def run(
    *args,
    # log level
    log_level: Literal['-q', '-s', '-v', '-vs'] = '-v',
    # case path
    case_path: Optional[str] = None,
    # html report
    html_report: bool = True,
    # allure
    allure: bool = True,
    allure_clear: bool = True,
    allure_serve: bool = False,
    # extra
    reruns: int = 0,
    maxfail: int = 0,
    x: bool = False,
    n: Union[Literal['auto', 'logical'], int] = 'auto',
    dist: Literal['load', 'loadscope', 'loadfile', 'loadgroup', 'worksteal', 'no'] = 'loadscope',
    strict_markers: bool = False,
    capture: bool = True,
    disable_warnings: bool = True,
    **kwargs,
) -> None:
    """
    运行 pytest 测试

    :param log_level: 控制台打印输出级别, 默认"-v"
    :param case_path: 指定测试用例函数, 默认为空，如果指定，则执行指定用例，否则执行全部
    :param html_report: 生成 HTML 测试报告, 默认开启
    :param allure: 生成 allure 测试报告, 默认开启
    :param allure_clear: 清空 allure 报告历史记录, 默认开启
    :param allure_serve: 自动打开 allure 测试报告服务， 默认关闭
    :param reruns: 用例运行失败重试次数, 兼容性差, 默认不开启使用
    :param maxfail: 用例运行失败数量，到达数量上限后终止运行，默认为 0，即不终止
    :param x: 用例运行失败, 终止运行, 默认关闭
    :param n: 分布式运行, 默认 "auto"
    :param dist: 分布式运行方式, 默认"loadscope", 详情: https://pytest-xdist.readthedocs.io/en/latest/distribution.html
    :param strict_markers: markers 严格模式, 对于使用了自定义 marker 的用例, 如果 marker 未在 pytest.ini 注册, 用例将报错
    :param capture: 避免在使用输出模式为"v"和"s"时，html报告中的表格日志为空的情况, 默认开启
    :param disable_warnings: 关闭控制台警告信息, 默认开启
    :return:
    """  # noqa: E501
    default_case_path = f'./testcases/{PROJECT_NAME}/'  # 默认执行指定项目下的所有测试用例
    if case_path is None:
        run_path = default_case_path
    else:
        if '::' not in case_path:
            raise ValueError(
                '用例收集失败, 请检查路径参数 \n'
                '类用例说明: \n'
                '\t1. 项目目录下没有多级目录: case_path = "文件名::类名" \n'
                '\t2. 项目目录下有多级目录: case_path = "目录名/.../文件名::类名" \n'
                '函数用例说明: \n'
                '\t1. 项目目录下没有多级目录: case_path = "文件名::类名::函数名" \n'
                '\t2. 项目目录下有多级目录: case_path = "目录名/.../文件名::函数名"'
            )
        run_path = default_case_path + case_path

    if html_report:
        if not os.path.exists(HTML_REPORT_PATH):
            os.makedirs(HTML_REPORT_PATH)

    is_html_report_file = (
        f'''--html={HTML_REPORT_PATH}\\{PROJECT_NAME}_{datetime.datetime.now().strftime(
            "%Y-%m-%d-%H_%M_%S")}.html'''
        if html_report
        else ''
    )

    is_html_report_self = '--self-contained-html' if html_report else ''

    is_allure = f'--alluredir={ALLURE_REPORT_PATH}' if allure else ''

    is_clear_allure = '--clean-alluredir' if is_allure and allure_clear else ''

    is_reruns = f'--reruns {reruns}' if reruns != 0 else ''  # noqa: F841

    is_maxfail = f'--maxfail={maxfail}' if maxfail != 0 else ''

    is_x = '-x' if x else ''

    is_n = f'-n={n}'  # noqa: F841

    is_dist = f'--dist={dist}'  # noqa: F841

    is_strict_markers = '--strict-markers' if strict_markers else ''

    is_capture = '--capture=tee-sys' if capture else ''

    is_disable_warnings = '--disable-warnings' if disable_warnings else ''

    kw = [f'{k}={v}' for k, v in kwargs.items()]

    run_args = [
        arg
        for arg in [
            f'{log_level}',
            f'{run_path}',
            f'{is_html_report_file}',
            f'{is_html_report_self}',
            f'{is_allure}',
            f'{is_clear_allure}'
            # f'{is_reruns}',
            f'{is_maxfail}',
            f'{is_x}',
            # f'{is_n}',  # 分布式运行存在诸多问题, 请谨慎使用
            # f'{is_dist}',
            f'{is_strict_markers}',
            f'{is_capture}',
            f'{is_disable_warnings}',
            *args,
        ]
        + kw
        if arg.strip() != ''
    ]
    run_args = list(set(run_args))

    format_run_args = []
    for i in run_args:
        if '=' in i:
            i_split = i.split('=')
            new_i = i.replace(i_split[1], '"' + f'{i_split[1]}' + '"')
            format_run_args.append(new_i)
        else:
            format_run_args.append(i)
    format_run_args_to_pytest_command = ' '.join(_ for _ in format_run_args)

    log.info(f'开始运行项目：{PROJECT_NAME}' if run_path == default_case_path else f'开始运行：{run_path}')
    log.info(f'Pytest 命令: pytest {format_run_args_to_pytest_command}')
    log.info('🚀 START')
    pytest.main(run_args)
    log.info('🏁 FINISH')

    yaml_report_files = os.listdir(YAML_REPORT_PATH)
    yaml_report_files.sort()
    test_result = read_yaml(YAML_REPORT_PATH, filename=yaml_report_files[-1])

    SendMail(test_result, is_html_report_file.split('=')[1]).send_report() if EMAIL_REPORT_SEND and html_report else ...

    DingTalk(test_result).send() if DING_TALK_REPORT_SEND else ...

    LarkTalk(test_result).send() if LARK_TALK_REPORT_SEND else ...

    shutil.copyfile(ALLURE_ENV_FILE, ALLURE_REPORT_ENV_FILE) if allure else ... if not os.path.exists(
        ALLURE_REPORT_ENV_FILE
    ) else ...

    os.popen(f'allure generate {ALLURE_REPORT_PATH} -o {ALLURE_REPORT_HTML_PATH} --clean') and os.popen(
        f'allure serve {ALLURE_REPORT_PATH}'
    ) if allure and allure_serve else ...


def main(*args, pydantic_verify: bool = True, **kwargs) -> None:
    """
    运行入口

    :param pydantic_verify: 用例数据完整架构 pydantic 快速检测, 默认开启
    :param args: pytest 运行参数
    :param kwargs: pytest 运行参数
    :return:
    """
    try:
        logo = """\n
         /$$   /$$ /$$$$$$$$ /$$$$$$$$ /$$$$$$$  /$$$$$$$$ /$$$$$$$  /$$$$$$$$
        | $$  | $$|__  $$__/|__  $$__/| $$__  $$| $$_____/| $$__  $$|__  $$__/
        | $$  | $$   | $$      | $$   | $$  | $$| $$      | $$  | $$   | $$   
        | $$$$$$$$   | $$      | $$   | $$$$$$$/| $$$$$   | $$$$$$$/   | $$   
        | $$__  $$   | $$      | $$   | $$____/ | $$__/   | $$____/    | $$   
        | $$  | $$   | $$      | $$   | $$      | $$      | $$         | $$   
        | $$  | $$   | $$      | $$   | $$      | $$      | $$         | $$   
        |__/  |__/   |__/      |__/   |__/      |__/      |__/         |__/   
    
            """
        print(logo)
        log.info(logo)
        redis_client.init()
        case_data.case_data_init(pydantic_verify)
        case_data.case_id_unique_verify()
        run(*args, **kwargs)
    except Exception as e:
        log.error(f'运行异常：{e}')
        import traceback

        SendMail({'error': traceback.format_exc()}).send_error()


if __name__ == '__main__':
    main()
