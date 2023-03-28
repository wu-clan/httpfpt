#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# 获取日志路径
LOG_PATH = os.path.join(BASE_DIR, 'log')

# 测试数据路径
TEST_DATA_PATH = os.path.join(BASE_DIR, 'data')

# Yaml测试数据路径
YAML_DATA_PATH = os.path.join(TEST_DATA_PATH, 'test_data', 'yaml_data')

# 测试报告路径
TEST_REPORT_PATH = os.path.join(BASE_DIR, 'report')

# allure测试报告路径
ALLURE_REPORT_PATH = os.path.join(TEST_REPORT_PATH, 'allure_report')

# allure html测试报告路径
ALLURE_REPORT_HTML_PATH = os.path.join(ALLURE_REPORT_PATH, 'html')

# HTML测试报告路径
HTML_REPORT_PATH = os.path.join(TEST_REPORT_PATH, 'html_report')

# HTML测试报告路径
HTML_EMAIL_REPORT_PATH = os.path.join(BASE_DIR, 'templates')

# YAML测试报告路径
YAML_REPORT_PATH = os.path.join(TEST_REPORT_PATH, 'yaml_report')

# allure环境文件
ALLURE_ENV_FILE = os.path.join(BASE_DIR, 'core', 'allure_env', 'environment.properties')

# allure报告环境文件，用作copy，避免allure开启清理缓存导致环境文件丢失
ALLURE_REPORT_ENV_FILE = os.path.join(ALLURE_REPORT_PATH, 'environment.properties')

# 运行环境文件路径
RUN_ENV_PATH = os.path.join(BASE_DIR, 'core', 'run_env')

# 测试用例路径
TEST_CASE_PATH = os.path.join(BASE_DIR, 'test_case')

# AUTH配置文件路径
AUTH_CONF_PATH = os.path.join(BASE_DIR, 'core')
