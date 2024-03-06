#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import os

from httpfpt.common.errors import ConfigInitError

__all__ = [
    'httpfpt_path',
    'set_httpfpt_dir',
]


class HttpFptPathConfig:
    def __init__(self, base_dir: str) -> None:
        """
        路径配置初始化

        :param base_dir:
        """
        self.base_dir = base_dir

    @property
    def project_dir(self) -> str:
        """项目根路径"""
        if not os.path.exists(self.base_dir):
            self.base_dir = os.getenv('HTTPFPT_PROJECT_PATH')
        if not self.base_dir:
            raise ConfigInitError(
                '运行失败：在访问 httpfpt API 前，请先通过 set_project_dir() 方法设置项目根路径，'
                '或配置 HTTPFPT_PROJECT_PATH 环境变量'
            )
        return self.base_dir

    @property
    def log_dir(self) -> str:
        """日志路径"""
        if not os.path.exists(self.base_dir):
            return os.path.join(os.path.expanduser('~'), '.httpfpt')
        return os.path.join(self.project_dir, 'log')

    @property
    def data_path(self) -> str:
        """数据路径"""
        return os.path.join(self.project_dir, 'data')

    @property
    def case_data_dir(self) -> str:
        """用例数据路径"""
        return os.path.join(self.data_path, 'test_data')

    @property
    def report_dir(self) -> str:
        """测试报告路径"""
        return os.path.join(self.project_dir, 'report')

    @property
    def allure_report_dir(self) -> str:
        """allure测试报告路径"""
        return os.path.join(self.report_dir, 'allure_report')

    @property
    def allure_html_report_dir(self) -> str:
        """allure html测试报告路径"""
        return os.path.join(self.allure_report_dir, 'html')

    @property
    def html_report_dir(self) -> str:
        """HTML测试报告路径"""
        return os.path.join(self.report_dir, 'html_report')

    @property
    def yaml_report_dir(self) -> str:
        """YAML测试报告路径"""
        return os.path.join(self.report_dir, 'yaml_report')

    @property
    def allure_env_file(self) -> str:
        """allure环境文件"""
        return os.path.join(self.project_dir, 'core', 'allure_env', 'environment.properties')

    @property
    def allure_report_env_file(self) -> str:
        """allure报告环境文件，用作copy，避免allure开启清理缓存导致环境文件丢失"""
        return os.path.join(self.allure_report_dir, 'environment.properties')

    @property
    def run_env_dir(self) -> str:
        """运行环境文件路径"""
        return os.path.join(self.project_dir, 'core', 'run_env')

    @property
    def testcase_dir(self) -> str:
        """测试用例路径"""
        return os.path.join(self.project_dir, 'testcases')

    @property
    def auth_conf_dir(self) -> str:
        """AUTH配置文件路径"""
        return os.path.join(self.project_dir, 'core')


def set_httpfpt_dir(base_dir: str) -> HttpFptPathConfig:
    """
    设置项目目录

    :param base_dir: 项目根路径
    :return:
    """
    global httpfpt_path

    httpfpt_path = HttpFptPathConfig(base_dir)
    return httpfpt_path


# global path_config
httpfpt_path: HttpFptPathConfig = set_httpfpt_dir('')
