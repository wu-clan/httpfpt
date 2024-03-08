#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from glom import glom

from httpfpt.common.errors import ConfigInitError
from httpfpt.core.path_conf import httpfpt_path

__all__ = ['httpfpt_config']


class HttpFptConfig:
    def __call__(self) -> HttpFptConfig:
        from httpfpt.common.toml_handler import read_toml

        self.settings = read_toml(httpfpt_path.settings_file_file)
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

        return self


set_httpfpt_config = HttpFptConfig()

# global config
httpfpt_config = set_httpfpt_config()
