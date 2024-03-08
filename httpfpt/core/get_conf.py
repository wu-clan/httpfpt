#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import os.path

from glom import glom

from httpfpt.common.errors import ConfigInitError
from httpfpt.core.path_conf import httpfpt_path

__all__ = ['httpfpt_config']


class HttpFptConfig:
    def __init__(self) -> None:
        # 项目目录名
        self.PROJECT_NAME = None
        # 测试报告
        self.TEST_REPORT_TITLE = None
        self.TESTER_NAME = None
        # mysql 数据库
        self.MYSQL_HOST = None
        self.MYSQL_PORT = None
        self.MYSQL_USER = None
        self.MYSQL_PASSWORD = None
        self.MYSQL_DATABASE = None
        self.MYSQL_CHARSET = None
        # redis 数据库
        self.REDIS_HOST = None
        self.REDIS_PORT = None
        self.REDIS_PASSWORD = None
        self.REDIS_DATABASE = None
        self.REDIS_TIMEOUT = None
        # 邮件
        self.EMAIL_SERVER = None
        self.EMAIL_PORT = None
        self.EMAIL_USER = None
        self.EMAIL_PASSWORD = None
        self.EMAIL_SEND_TO = None
        self.EMAIL_SSL = None
        self.EMAIL_SEND = None
        # 钉钉
        self.DINGDING_WEBHOOK = None
        self.DINGDING_PROXY = None
        self.DINGDING_SEND = None
        # 飞书
        self.FEISHU_WEBHOOK = None
        self.FEISHU_PROXY = None
        self.FEISHU_SEND = None
        # 请求发送
        self.REQUEST_TIMEOUT = None
        self.REQUEST_VERIFY = None
        self.REQUEST_REDIRECTS = None
        self.REQUEST_PROXIES_REQUESTS = None
        self.REQUEST_PROXIES_HTTPX = None
        self.REQUEST_RETRY = None

    def __call__(self, settings: str | dict, config_filename: str | None = None) -> HttpFptConfig:
        """
        设置项目配置

        :param settings: 项目配置，字典或指定 toml 配置文件
        :param config_filename:
        :return:
        """
        if isinstance(settings, str):
            from httpfpt.common.toml_handler import read_toml

            if not os.path.isdir(settings) and not os.path.isfile(settings):
                raise ConfigInitError('配置获取失败，请检查配置文件路径是否合法')
            self.settings = read_toml(settings, config_filename)
        else:
            self.settings = settings
        try:
            self.PROJECT_NAME = glom(self.settings, 'project.name')
            self.TEST_REPORT_TITLE = glom(self.settings, 'report.title')
            self.TESTER_NAME = glom(self.settings, 'report.tester_name')
            self.MYSQL_HOST = glom(self.settings, 'mysql.host')
            self.MYSQL_PORT = glom(self.settings, 'mysql.port')
            self.MYSQL_USER = glom(self.settings, 'mysql.user')
            self.MYSQL_PASSWORD = glom(self.settings, 'mysql.password')
            self.MYSQL_DATABASE = glom(self.settings, 'mysql.database')
            self.MYSQL_CHARSET = glom(self.settings, 'mysql.charset')
            self.REDIS_HOST = glom(self.settings, 'redis.host')
            self.REDIS_PORT = glom(self.settings, 'redis.port')
            self.REDIS_PASSWORD = glom(self.settings, 'redis.password')
            self.REDIS_DATABASE = glom(self.settings, 'redis.database')
            self.REDIS_TIMEOUT = glom(self.settings, 'redis.timeout')
            self.EMAIL_SERVER = glom(self.settings, 'email.host')
            self.EMAIL_PORT = glom(self.settings, 'email.port')
            self.EMAIL_USER = glom(self.settings, 'email.user')
            self.EMAIL_PASSWORD = glom(self.settings, 'email.password')
            self.EMAIL_SEND_TO = glom(self.settings, 'email.receiver')
            self.EMAIL_SSL = glom(self.settings, 'email.ssl')
            self.EMAIL_SEND = glom(self.settings, 'email.send')
            self.DINGDING_WEBHOOK = glom(self.settings, 'ding.webhook')
            self.DINGDING_PROXY = {
                'http': glom(self.settings, 'ding.proxies.http')
                if glom(self.settings, 'ding.proxies.http') != ''
                else None,
                'https': glom(self.settings, 'ding.proxies.https')
                if glom(self.settings, 'ding.proxies.https') != ''
                else None,
            }
            self.DINGDING_SEND = glom(self.settings, 'ding.send')
            self.FEISHU_WEBHOOK = glom(self.settings, 'lark.webhook')
            self.FEISHU_PROXY = {
                'http': glom(self.settings, 'lark.proxies.http')
                if glom(self.settings, 'lark.proxies.http') != ''
                else None,
                'https': glom(self.settings, 'lark.proxies.https')
                if glom(self.settings, 'lark.proxies.https') != ''
                else None,
            }
            self.FEISHU_SEND = glom(self.settings, 'lark.send')
            self.REQUEST_TIMEOUT = glom(self.settings, 'request.timeout')
            self.REQUEST_VERIFY = glom(self.settings, 'request.verify')
            self.REQUEST_REDIRECTS = glom(self.settings, 'request.redirects')
            self.REQUEST_PROXIES_REQUESTS = {
                'http': glom(self.settings, 'request.proxies.http')
                if glom(self.settings, 'request.proxies.http') != ''
                else None,
                'https': glom(self.settings, 'request.proxies.https')
                if glom(self.settings, 'request.proxies.https') != ''
                else None,
            }
            self.REQUEST_PROXIES_HTTPX = {
                'http://': glom(self.settings, 'request.proxies.http')
                if glom(self.settings, 'request.proxies.http') != ''
                else None,
                'https://': glom(self.settings, 'request.proxies.https')
                if glom(self.settings, 'request.proxies.https') != ''
                else None,
            }
            self.REQUEST_RETRY = glom(self.settings, 'request.retry')
        except KeyError as e:
            raise ConfigInitError(f'配置解析失败：缺失参数 {str(e)}，请核对配置文件或字典')

        conf = HttpFptConfig()
        return conf


set_httpfpt_config = HttpFptConfig()

# global config
httpfpt_config = set_httpfpt_config(httpfpt_path.settings_file_file)
