#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from datetime import datetime

import pytest
from _pytest.logging import LogCaptureFixture
from filelock import FileLock
from loguru import logger
from py._xmlgen import html

from fastpt.common.log import log
from fastpt.core.get_conf import TESTER_NAME, PROJECT_NAME, HTML_REPORT_TITLE


@pytest.fixture(scope='session', autouse=True)
def session_fixture(tmp_path_factory, worker_id):
    # 避免分布式执行用例循环执行此fixture
    # 例子: https://www.yuque.com/poloyy/nz6yd2/wq3mby#MXI0w
    # 优化例子: https://www.yuque.com/poloyy/nz6yd2/wq3mby#UYgcL
    if worker_id == "master":
        return None

    # get the temp directory shared by all workers
    root_tmp_dir = tmp_path_factory.getbasetemp().parent

    fn = root_tmp_dir / "data.json"
    with FileLock(str(fn) + ".lock"):
        if fn.is_file():
            data = json.loads(fn.read_text())
        else:
            data = None
            fn.write_text(json.dumps(data))
    return data


@pytest.fixture(scope='package', autouse=True)
def package_fixture():
    ...
    yield
    log.info('测试用例执行结束')


@pytest.fixture(scope='module', autouse=True)
def module_fixture():
    ...
    yield
    ...


@pytest.fixture(scope='class', autouse=True)
def class_fixture():
    ...
    yield
    ...


@pytest.fixture(scope='function', autouse=True)
def function_fixture(request):
    log.info(f'----------------- Running case func: {request.function.__name__} -----------------')

    def log_end():
        log.info('end \n')

    request.addfinalizer(log_end)  # teardown终结函数 == yield后的代码


@pytest.fixture(autouse=True)
def caplog(caplog: LogCaptureFixture):
    """
    将 pytest 的 caplog 夹具默认日志记录器改为 loguru,而非默认 logging

    :param caplog:
    :return:
    """
    handler_id = logger.add(caplog.handler, format="{message}")
    yield caplog
    logger.remove(handler_id)


def pytest_configure(config):
    """
    html报告环境信息配置

    :param config:
    :return:
    """
    # 添加接口地址与项目名称
    config._metadata["Project Name"] = PROJECT_NAME
    # config._metadata.pop("JAVA_HOME")
    config._metadata.pop("Packages")
    config._metadata.pop("Platform")
    config._metadata.pop("Plugins")


def pytest_html_results_summary(prefix):
    """
    html报告摘要信息配置

    :param prefix:
    :return:
    """
    # 向html报告中的summary添加额外信息
    # prefix.extend([html.p(f"Department:")])
    prefix.extend([html.p(f"Tester: {TESTER_NAME}")])


@pytest.mark.optionalhook
def pytest_html_report_title(report):
    report.title = f"{HTML_REPORT_TITLE}"


@pytest.mark.optionalhook
def pytest_html_results_table_header(cells):
    """
    html报告表格列配置

    :param cells:
    :return:
    """
    cells.insert(1, html.th('Description'))
    cells.insert(3, html.th('Execute Time', class_='sortable time', col='time'))
    cells.pop()


@pytest.mark.optionalhook
def pytest_html_results_table_row(report, cells):
    """
    html报告表格列值配置

    :param report:
    :param cells:
    :return:
    """
    cells.insert(1, html.td(getattr(report, 'description', None)))
    cells.insert(3, html.td(datetime.utcnow(), class_='col-time'))
    cells.pop()


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    """
    自动化获取用例描述, 解决测试用例参数包含中文问题

    :param item:
    :param call:
    :return:
    """
    outcome = yield
    report = outcome.get_result()
    # 获取用例描述
    if getattr(item.function, '__doc__', None) is None:
        report.description = str(item.function.__name__)
    else:
        report.description = str(item.function.__doc__)


def pytest_collection_modifyitems(items) -> None:
    """
    解决数据驱动ids参数为中文时,控制台输出乱码问题

    :param items:
    :return:
    """
    # item表示每个用例
    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        # 打开此注释可以解决控制台ids乱码问题,但是会影响报告中的ids参数乱码
        # 问题在这里: https://github.com/pytest-dev/pytest-html/issues/450
        # item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")
