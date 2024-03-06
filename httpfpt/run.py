#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import shutil
import sys

from typing import Literal

import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from httpfpt.common.log import log
from httpfpt.common.yaml_handler import read_yaml
from httpfpt.core.get_conf import config
from httpfpt.core.path_conf import httpfpt_path_config
from httpfpt.db.redis_db import redis_client
from httpfpt.utils.request import case_data_parse as case_data
from httpfpt.utils.send_report.ding_talk import DingTalk
from httpfpt.utils.send_report.lark_talk import LarkTalk
from httpfpt.utils.send_report.send_email import SendMail
from httpfpt.utils.time_control import get_current_time


def startup(
    *args,
    log_level: Literal['-q', '-s', '-v', '-vv'],
    case_path: str | None,
    html_report: bool,
    allure: bool,
    allure_clear: bool,
    allure_serve: bool,
    maxfail: int,
    x: bool,
    strict_markers: bool,
    capture: bool,
    disable_warnings: bool,
    **kwargs,
) -> None:
    """运行启动程序"""
    run_args = [log_level]

    default_case_path = os.sep.join([os.path.dirname(__file__), 'testcases', config.PROJECT_NAME])
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

    html_report_filename = f'{config.PROJECT_NAME}_{get_current_time("%Y-%m-%d %H_%M_%S")}.html'
    if html_report:
        if not os.path.exists(httpfpt_path_config.html_report_dir):
            os.makedirs(httpfpt_path_config.html_report_dir)
        run_args.extend(
            (
                f'--html={os.path.join(httpfpt_path_config.html_report_dir, html_report_filename)}',
                '--self-contained-html',
            )
        )

    if allure:
        run_args.append(f'--alluredir={httpfpt_path_config.allure_report_dir}')
        if allure_clear:
            run_args.append('--clean-alluredir')

    if maxfail != 0:
        run_args.append(f'--maxfail {maxfail}')

    if x:
        run_args.append('-x')

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

    log.info(f'开始运行项目：{config.PROJECT_NAME}' if run_path == default_case_path else f'开始运行：{run_path}')
    log.info(f'Pytest CLI: pytest {run_pytest_command_args}')
    log.info('🚀 START')
    pytest.main(run_args)
    log.info('🏁 FINISH')

    yaml_report_files = os.listdir(httpfpt_path_config.yaml_report_dir)
    yaml_report_files.sort()
    test_result = read_yaml(httpfpt_path_config.yaml_report_dir, filename=yaml_report_files[-1])

    if html_report and config.EMAIL_REPORT_SEND:
        SendMail(test_result, html_report_filename).send_report()

    if config.DING_TALK_REPORT_SEND:
        DingTalk(test_result).send()

    if config.LARK_TALK_REPORT_SEND:
        LarkTalk(test_result).send()

    if allure:
        if not os.path.exists(httpfpt_path_config.allure_report_env_file):
            shutil.copyfile(httpfpt_path_config.allure_env_file, httpfpt_path_config.allure_report_env_file)

    if allure and allure_serve:
        os.popen(
            f'allure generate {httpfpt_path_config.allure_report_dir} -o {httpfpt_path_config.allure_html_report_dir} '
            + '--clean'
        ) and os.popen(f'allure serve {httpfpt_path_config.allure_report_dir}')  # type: ignore


def run(
    *args,
    # init
    clean_cache: bool = False,
    pydantic_verify: bool = True,
    # log level
    log_level: Literal['-q', '-s', '-v', '-vv'] = '-v',
    # case path
    case_path: str | None = None,
    # html report
    html_report: bool = True,
    # allure
    allure: bool = True,
    allure_clear: bool = True,
    allure_serve: bool = False,
    # extra
    maxfail: int = 0,
    x: bool = False,
    strict_markers: bool = False,
    capture: bool = True,
    disable_warnings: bool = True,
    **kwargs,
) -> None:
    """
    运行入口

    :param args: pytest 运行参数
    :param clean_cache: 清理 redis 缓存数据，对于脏数据，这很有用，默认关闭
    :param pydantic_verify: 用例数据完整架构 pydantic 快速检测, 默认开启
    :param args: pytest 运行参数
    :param log_level: 控制台打印输出级别, 默认"-v"
    :param case_path: 指定当前项目下的测试用例函数, 默认为空，如果指定，则执行指定用例，否则执行全部
    :param html_report: 生成 HTML 测试报告, 默认开启
    :param allure: 生成 allure 测试报告, 默认开启
    :param allure_clear: 清空 allure 报告历史记录, 默认开启
    :param allure_serve: 自动打开 allure 测试报告服务， 默认关闭
    :param maxfail: 用例运行失败数量，到达数量上限后终止运行，默认为 0，即不终止
    :param x: 用例运行失败, 终止运行, 默认关闭
    :param strict_markers: markers 严格模式, 对于设置 marker 装饰器的用例, 如果 marker 未在 pytest.ini 注册, 用例将报错
    :param capture: 避免在使用输出模式为"v"和"s"时，html报告中的表格日志为空的情况, 默认开启
    :param disable_warnings: 关闭控制台警告信息, 默认开启
    :param kwargs: pytest 运行关键字参数
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
        log.info(logo)
        redis_client.init()
        case_data.clean_cache_data(clean_cache)
        case_data.case_data_init(pydantic_verify)
        case_data.case_id_unique_verify()
        startup(
            *args,
            log_level=log_level,
            case_path=case_path,
            html_report=html_report,
            allure=allure,
            allure_clear=allure_clear,
            allure_serve=allure_serve,
            maxfail=maxfail,
            x=x,
            strict_markers=strict_markers,
            capture=capture,
            disable_warnings=disable_warnings,
            **kwargs,
        )
    except Exception as e:
        log.error(f'运行异常：{e}')
        import traceback

        SendMail({'error': traceback.format_exc()}).send_error()
