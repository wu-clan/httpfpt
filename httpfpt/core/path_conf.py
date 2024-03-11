#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import os

from httpfpt.common.errors import ConfigInitError

__all__ = ['httpfpt_path']


class HttpFptPathConfig:
    @property
    def project_dir(self) -> str:
        """项目根路径"""
        _base_dir = os.getenv('HTTPFPT_PROJECT_PATH')
        if not _base_dir:
            raise ConfigInitError(
                '运行失败：在访问 HTTPFPT API 前，请先通过 `httpfpt` 命令创建新项目；'
                '如果已经创建，请确保配置了 `HTTPFPT_PROJECT_PATH` 环境变量为项目目录'
            )
        else:
            if not os.path.exists(_base_dir):
                raise ConfigInitError(f"""
                错误：操作失败 - 未找到项目路径 '{_base_dir}'。
                请确保以下几点：
                1. 环境变量是否已正确配置
                2. 检查指定的项目路径是否存在。如果项目还未创建，你需要先创建一个新项目
                完成上述检查后，请重新尝试执行此操作
                """)
        return _base_dir

    @property
    def log_dir(self) -> str:
        """日志路径"""
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

    @property
    def settings_file_file(self) -> str:
        """核心配置文件路径"""
        return os.path.join(self.project_dir, 'core', 'conf.toml')


# global path_config
httpfpt_path = HttpFptPathConfig()
