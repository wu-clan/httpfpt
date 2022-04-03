#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

import pytest
from _pytest.logging import LogCaptureFixture
from filelock import FileLock
from loguru import logger
from py._xmlgen import html

from fastpt.common.log import log
from fastpt.core.get_conf import TESTER_NAME, PROJECT_NAME


@pytest.fixture(scope='session', autouse=True)
def session_fixture() -> None:
    # 避免分布式执行用例循环执行此fixture
    with FileLock("session.lock"):
        ...
    yield
    ...


@pytest.fixture(scope='package', autouse=True)
def package_fixture() -> None:
    ...
    yield
    log.info('测试用例执行结束')


@pytest.fixture(scope='module', autouse=True)
def module_fixture() -> None:
    ...
    yield
    ...


@pytest.fixture(scope='class', autouse=True)
def class_fixture() -> None:
    ...
    yield
    ...


@pytest.fixture(scope='function', autouse=True)
def function_fixture(request) -> None:
    log.info(f'----------------- Running case: {request.function.__name__} -----------------')

    def log_end():
        log.info('end \n')

    request.addfinalizer(log_end)  # teardown终结函数 == yield后的代码


@pytest.fixture(autouse=True)
def caplog(caplog: LogCaptureFixture):
    # 将 pytest 的 caplog 夹具默认日志记录器改为 loguru,而非默认 logging
    handler_id = logger.add(caplog.handler, format="{message}")
    yield caplog
    logger.remove(handler_id)


# html报告环境信息配置
def pytest_configure(config):
    # 添加接口地址与项目名称
    config._metadata["Project Name"] = PROJECT_NAME
    # config._metadata['Test Address'] =
    # 删除Java_Home
    config._metadata.pop("JAVA_HOME")


# html报告摘要信息配置
def pytest_html_results_summary(prefix) -> None:
    # 向html报告中的summary添加额外信息
    # prefix.extend([html.p(f"Department:")])
    prefix.extend([html.p(f"Tester: {TESTER_NAME}")])


# html报告表格列配置
@pytest.mark.optionalhook
def pytest_html_results_table_header(cells):
    cells.insert(1, html.th('Description'))
    cells.insert(3, html.th('Time', class_='sortable time', col='time'))
    cells.pop()


# html报告表格列值配置
@pytest.mark.optionalhook
def pytest_html_results_table_row(report, cells):
    cells.insert(1, html.td(report.description))
    cells.insert(3, html.td(datetime.utcnow(), class_='col-time'))
    cells.pop()


# 自动化获取用例描述, 解决测试用例参数包含中文问题
@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if item.function.__doc__ is None:
        report.description = str(item.function.__name__)
    else:
        report.description = str(item.function.__doc__)


# 解决数据驱动ids参数为中文时,控制台输出乱码
def pytest_collection_modifyitems(items) -> None:
    # item表示每个用例
    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")
