#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

__all__ = ['path_config', 'init_path_config']

# global path_config
path_config = None


class HttpFptPathConfig:
    def __init__(self, base_dir: str) -> None:
        """
        路径配置初始化

        :param base_dir:
        """
        self.BASE_DIR = base_dir
        # 获取日志路径
        self.LOG_PATH = os.path.join(self.BASE_DIR, 'log')
        # 测试数据路径
        self.TEST_DATA_PATH = os.path.join(self.BASE_DIR, 'data')
        # Yaml测试数据路径
        self.CASE_DATA_PATH = os.path.join(self.TEST_DATA_PATH, 'test_data')
        # 测试报告路径
        self.TEST_REPORT_PATH = os.path.join(self.BASE_DIR, 'report')
        # allure测试报告路径
        self.ALLURE_REPORT_PATH = os.path.join(self.TEST_REPORT_PATH, 'allure_report')
        # allure html测试报告路径
        self.ALLURE_REPORT_HTML_PATH = os.path.join(self.ALLURE_REPORT_PATH, 'html')
        # HTML测试报告路径
        self.HTML_REPORT_PATH = os.path.join(self.TEST_REPORT_PATH, 'html_report')
        # YAML测试报告路径
        self.YAML_REPORT_PATH = os.path.join(self.TEST_REPORT_PATH, 'yaml_report')
        # allure环境文件
        self.ALLURE_ENV_FILE = os.path.join(self.BASE_DIR, 'core', 'allure_env', 'environment.properties')
        # allure报告环境文件，用作copy，避免allure开启清理缓存导致环境文件丢失
        self.ALLURE_REPORT_ENV_FILE = os.path.join(self.ALLURE_REPORT_PATH, 'environment.properties')
        # 运行环境文件路径
        self.RUN_ENV_PATH = os.path.join(self.BASE_DIR, 'core', 'run_env')
        # 测试用例路径
        self.TEST_CASE_PATH = os.path.join(self.BASE_DIR, 'testcases')
        # AUTH配置文件路径
        self.AUTH_CONF_PATH = os.path.join(self.BASE_DIR, 'core')


def init_path_config(base_dir: str) -> None:
    """
    初始化配置

    :param base_dir: 项目根目录
    :return:
    """
    global path_config

    path_config = HttpFptPathConfig(base_dir)
