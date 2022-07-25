#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from fastpt.core.get_conf import PROJECT_NAME

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# 测试用例路径
TESTCASE_PATH = os.path.join(BASE_DIR, 'test_case', PROJECT_NAME)

# 测试数据路径
TEST_DATA_PATH = os.path.join(BASE_DIR, 'data')

# Excel测试数据路径
EXCEL_DATA_PATH = os.path.join(TEST_DATA_PATH, 'test_data', 'excel_data')

# Yaml测试数据路径
YAML_DATA_PATH = os.path.join(TEST_DATA_PATH, 'test_data', 'yaml_data')

# 测试报告路径
TEST_REPORT_PATH = os.path.join(BASE_DIR, 'report')

# allure测试报告路径
ALLURE_REPORT_PATH = os.path.join(TEST_REPORT_PATH, 'allure_report')

# EXCEL测试报告路径
EXCEL_REPORT_PATH = os.path.join(TEST_REPORT_PATH, 'excel_report')

# HTML测试报告路径
HTML_REPORT_PATH = os.path.join(TEST_REPORT_PATH, 'html_report')

# YAML测试报告路径
YAML_REPORT_PATH = os.path.join(TEST_REPORT_PATH, 'yaml_report')

# allure环境文件
ALLURE_ENV_FILE = os.path.join(BASE_DIR, 'core', 'allure_env', 'environment.properties')

# allure报告环境文件，用作copy，避免allure开启清理缓存导致环境文件丢失
ALLURE_REPORT_ENV_FILE = os.path.join(ALLURE_REPORT_PATH, 'environment.properties')
