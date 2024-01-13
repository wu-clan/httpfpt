#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

from datetime import datetime, timedelta

import pytest

from filelock import FileLock
from py._xmlgen import html

from httpfpt.common.log import log
from httpfpt.common.variable_cache import variable_cache
from httpfpt.common.yaml_handler import write_yaml_report
from httpfpt.core.get_conf import config as sys_config


@pytest.fixture(scope='session', autouse=True)
def session_fixture(tmp_path_factory, worker_id):
    # 避免分布式执行用例循环执行此fixture
    data = 'some data'
    if worker_id == 'master':
        return data
    root_tmp_dir = tmp_path_factory.getbasetemp().parent
    fn = root_tmp_dir / 'data.txt'
    with FileLock(str(fn) + '.lock'):
        if fn.is_file():
            data = fn.read_text('utf-8')
        else:
            fn.write_text(data, 'utf-8')
    return data


@pytest.fixture(scope='package', autouse=True)
def package_fixture():
    yield
    # 预留空行
    log.info('')
    # 清理临时变量
    variable_cache.clear()


@pytest.fixture(scope='module', autouse=True)
def module_fixture():
    pass


@pytest.fixture(scope='class', autouse=True)
def class_fixture():
    pass


@pytest.fixture(scope='function', autouse=True)
def function_fixture(request):
    log.info('')  # 预留空行
    log.info(f'🔥 Running: {request.function.__name__}')

    def testcase_end():
        log.info('🔚 End')

    # teardown终结函数 == yield后的代码
    request.addfinalizer(testcase_end)


def pytest_configure(config):
    """
    pytest配置

    :param config:
    :return:
    """
    # 元信息配置
    metadata = config.pluginmanager.getplugin('metadata')
    if metadata:
        from pytest_metadata.plugin import metadata_key

        config.stash[metadata_key]['Project Name'] = sys_config.PROJECT_NAME
        del config.stash[metadata_key]['Packages']
        del config.stash[metadata_key]['Platform']
        del config.stash[metadata_key]['Plugins']


def pytest_html_results_summary(prefix):
    """
    html报告摘要信息配置

    :param prefix:
    :return:
    """
    # 向 html 报告中的 summary 添加额外信息
    prefix.extend([html.p(f'Tester: {sys_config.TESTER_NAME}')])


@pytest.mark.optionalhook
def pytest_html_report_title(report):
    """
    html报告标题配置

    :param report:
    :return:
    """
    report.title = f'{sys_config.TEST_REPORT_TITLE}'


@pytest.mark.optionalhook
def pytest_html_results_table_header(cells):
    """
    html报告表格列配置

    :param cells:
    :return:
    """
    cells.insert(1, html.th('Description'))
    cells.insert(3, html.th('Start Time', class_='sortable time', col='time'))
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
    cells.insert(3, html.td(datetime.now(), class_='col-time'))
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


def pytest_collection_modifyitems(items):
    """
    解决数据驱动ids参数为中文时,控制台输出乱码问题

    :param items:
    :return:
    """
    # item表示每个用例
    for item in items:
        item.name = item.name.encode('utf-8').decode('unicode_escape')
        item._nodeid = item.nodeid.encode('utf-8').decode('unicode_escape')


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    收集测试结果
    """
    started_time = terminalreporter._sessionstarttime
    elapsed_seconds = float(time.time() - started_time)
    hours, remainder = divmod(elapsed_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    total = terminalreporter._numcollected
    stats = terminalreporter.stats
    passed = len(stats.get('passed', []))
    failed = len(stats.get('failed', []))
    error = len(stats.get('error', []))
    skipped = len(stats.get('skipped', []))
    data = {
        'result': 'Success' if failed == 0 else 'Failed',
        'total': total,
        'passed': passed,
        'failed': failed,
        'error': error,
        'skipped': skipped,
        'started_time': datetime.fromtimestamp(started_time).strftime('%Y-%m-%d %H:%M:%S'),
        'elapsed': f'{int(hours):02}:{int(minutes):02}:{int(seconds):02}',
    }
    write_yaml_report(data=data)
