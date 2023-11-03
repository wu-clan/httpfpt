#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import shutil
import sys

from typing import Literal, Optional, Union

import pytest

sys.path.append('..')

from httpfpt.common.log import log
from httpfpt.common.yaml_handler import read_yaml
from httpfpt.core.get_conf import DING_TALK_REPORT_SEND, EMAIL_REPORT_SEND, LARK_TALK_REPORT_SEND, PROJECT_NAME
from httpfpt.core.path_conf import (
    ALLURE_ENV_FILE,
    ALLURE_REPORT_ENV_FILE,
    ALLURE_REPORT_HTML_PATH,
    ALLURE_REPORT_PATH,
    HTML_REPORT_PATH,
    YAML_REPORT_PATH,
)
from httpfpt.db.redis_db import redis_client
from httpfpt.utils.request import case_data_parse as case_data
from httpfpt.utils.send_report.ding_talk import DingTalk
from httpfpt.utils.send_report.lark_talk import LarkTalk
from httpfpt.utils.send_report.send_email import SendMail
from httpfpt.utils.time_control import get_current_time


def startup(
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
    n: Union[Literal['auto', 'logical'], int, None] = None,
    dist: Union[Literal['load', 'loadscope', 'loadfile', 'loadgroup', 'worksteal', 'no'], None] = None,
    strict_markers: bool = False,
    capture: bool = True,
    disable_warnings: bool = True,
    **kwargs,
) -> None:
    """
    运行启动程序

    :param log_level: 控制台打印输出级别, 默认"-v"
    :param case_path: 指定测试用例函数, 默认为空，如果指定，则执行指定用例，否则执行全部
    :param html_report: 生成 HTML 测试报告, 默认开启
    :param allure: 生成 allure 测试报告, 默认开启
    :param allure_clear: 清空 allure 报告历史记录, 默认开启
    :param allure_serve: 自动打开 allure 测试报告服务， 默认关闭
    :param reruns: 用例运行失败重试次数, 兼容性差, 默认不开启使用
    :param maxfail: 用例运行失败数量，到达数量上限后终止运行，默认为 0，即不终止
    :param x: 用例运行失败, 终止运行, 默认关闭
    :param n: 分布式运行, 默认关闭
    :param dist: 分布式运行方式, 默认关闭, 详情: https://pytest-xdist.readthedocs.io/en/latest/distribution.html
    :param strict_markers: markers 严格模式, 对于使用了自定义 marker 的用例, 如果 marker 未在 pytest.ini 注册, 用例将报错
    :param capture: 避免在使用输出模式为"v"和"s"时，html报告中的表格日志为空的情况, 默认开启
    :param disable_warnings: 关闭控制台警告信息, 默认开启
    :return:
    """  # noqa: E501
    run_args = [log_level]

    default_case_path = os.sep.join([os.path.dirname(__file__), 'testcases', PROJECT_NAME])
    if case_path:
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
        sep = os.path.sep
        case_path = case_path.replace('/', sep)
        run_path = os.sep.join([default_case_path, case_path])
    else:
        run_path = default_case_path
    run_args.append(run_path)

    html_report_filename = f'{PROJECT_NAME}_{get_current_time("%Y-%m-%d %H_%M_%S")}.html'
    if html_report:
        if not os.path.exists(HTML_REPORT_PATH):
            os.makedirs(HTML_REPORT_PATH)
        run_args.append(f'--html={os.path.join(HTML_REPORT_PATH, html_report_filename)}')
        run_args.append('--self-contained-html')

    if allure:
        run_args.append(f'--alluredir={ALLURE_REPORT_PATH}')
        if allure_clear:
            run_args.append('--clean-alluredir')

    if reruns != 0:
        run_args.append(f'--reruns {reruns}')

    if maxfail != 0:
        run_args.append(f'--maxfail {maxfail}')

    if x:
        run_args.append('-x')

    if n:
        run_args.append(f'-n={n}')

    if dist:
        run_args.append(f'--dist={dist}')

    if strict_markers:
        run_args.append('--strict-markers')

    if capture:
        run_args.append('--capture=tee-sys')

    if disable_warnings:
        run_args.append('--disable-warnings')

    if len(args) > 0:
        for i in args:
            if i not in run_args:
                run_args.append(i)
    if len(kwargs) > 0:
        for k, v in kwargs.items():
            for i in run_args:
                if '=' in i and k in i:
                    run_args.remove(i)
                    run_args.append(f'{k}={v}')
    run_args = list(set(run_args))
    format_run_args = []
    for i in run_args:
        if '=' in i:
            i_split = i.split('=')
            new_i = i.replace(i_split[1], '"' + f'{i_split[1]}' + '"')
            format_run_args.append(new_i)
        else:
            format_run_args.append(i)
    run_pytest_command_args = ' '.join(_ for _ in format_run_args)

    log.info(f'开始运行项目：{PROJECT_NAME}' if run_path == default_case_path else f'开始运行：{run_path}')
    log.info(f'Pytest CLI: pytest {run_pytest_command_args}')
    log.info('🚀 START')
    pytest.main(run_args)
    log.info('🏁 FINISH')

    yaml_report_files = os.listdir(YAML_REPORT_PATH)
    yaml_report_files.sort()
    test_result = read_yaml(YAML_REPORT_PATH, filename=yaml_report_files[-1])

    if html_report and EMAIL_REPORT_SEND:
        SendMail(test_result, html_report_filename).send_report()

    if DING_TALK_REPORT_SEND:
        DingTalk(test_result).send()

    if LARK_TALK_REPORT_SEND:
        LarkTalk(test_result).send()

    if allure:
        if not os.path.exists(ALLURE_REPORT_ENV_FILE):
            shutil.copyfile(ALLURE_ENV_FILE, ALLURE_REPORT_ENV_FILE)

    if allure and allure_serve:
        os.popen(f'allure generate {ALLURE_REPORT_PATH} -o {ALLURE_REPORT_HTML_PATH} --clean') and os.popen(
            f'allure serve {ALLURE_REPORT_PATH}'
        )  # type: ignore


def run(*args, pydantic_verify: bool = True, **kwargs) -> None:
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
        | $$$$$$$$   | $$      | $$   | $$$$$$$/| $$$$$$  | $$$$$$$/   | $$   
        | $$__  $$   | $$      | $$   | $$____/ | $$___/  | $$____/    | $$   
        | $$  | $$   | $$      | $$   | $$      | $$      | $$         | $$   
        | $$  | $$   | $$      | $$   | $$      | $$      | $$         | $$   
        |__/  |__/   |__/      |__/   |__/      |__/      |__/         |__/   
    
            """
        print(logo)
        log.info(logo)
        redis_client.init()
        case_data.case_data_init(pydantic_verify)
        case_data.case_id_unique_verify()
        startup(*args, **kwargs)
    except Exception as e:
        log.error(f'运行异常：{e}')
        import traceback

        SendMail({'error': traceback.format_exc()}).send_error()


if __name__ == '__main__':
    run()
