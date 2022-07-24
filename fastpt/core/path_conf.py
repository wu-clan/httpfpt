#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from fastpt.core.get_conf import PROJECT_NAME

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# 测试用例路径
TESTCASE_PATH = os.path.join(BASE_DIR, 'test_case', PROJECT_NAME)

# Excel测试数据路径
EXCEL_DATA_PATH = os.path.join(BASE_DIR, 'data', 'test_data', 'excel_data')

# Yaml测试数据路径
YAML_DATA_PATH = os.path.join(BASE_DIR, 'data', 'test_data', 'yaml_data')

# Yaml全局变量路径
YAML_VARS_PATH = os.path.join(BASE_DIR, 'data', 'global_data')

# allure测试报告路径
ALLURE_REPORT_PATH = os.path.join(BASE_DIR, 'report', 'allure_report')

# EXCEL测试报告路径
EXCEL_REPORT_PATH = os.path.join(BASE_DIR, 'report', 'excel_report')

# HTML测试报告路径
HTML_REPORT_PATH = os.path.join(BASE_DIR, 'report', 'html_report')

# YAML测试报告路径
YAML_REPORT_PATH = os.path.join(BASE_DIR, 'report', 'yaml_report')

# allure env file
ALLURE_ENV_FILE = os.path.join(BASE_DIR, 'core', 'allure_env', 'environment.properties')
ALLURE_REPORT_ENV_FILE = os.path.join(ALLURE_REPORT_PATH, 'environment.properties')
