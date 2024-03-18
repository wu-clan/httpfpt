#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functools import lru_cache
from pathlib import Path

from glom import glom

from httpfpt.common.toml_handler import read_toml


class HttpFptConfig:
    def __init__(self) -> None:
        self._config = read_toml(str(Path(__file__).resolve().parent), 'conf.toml')

        # 项目目录名
        self.PROJECT_NAME = glom(self._config, 'project.name')

        # 测试报告
        self.TEST_REPORT_TITLE = glom(self._config, 'report.title')
        self.TESTER_NAME = glom(self._config, 'report.tester_name')

        # mysql 数据库
        self.MYSQL_HOST = glom(self._config, 'mysql.host')
        self.MYSQL_PORT = glom(self._config, 'mysql.port')
        self.MYSQL_USER = glom(self._config, 'mysql.user')
        self.MYSQL_PASSWORD = glom(self._config, 'mysql.password')
        self.MYSQL_DATABASE = glom(self._config, 'mysql.database')
        self.MYSQL_CHARSET = glom(self._config, 'mysql.charset')

        # redis 数据库
        self.REDIS_HOST = glom(self._config, 'redis.host')
        self.REDIS_PORT = glom(self._config, 'redis.port')
        self.REDIS_PASSWORD = glom(self._config, 'redis.password')
        self.REDIS_DATABASE = glom(self._config, 'redis.database')
        self.REDIS_TIMEOUT = glom(self._config, 'redis.timeout')

        # 邮件
        self.EMAIL_SERVER = glom(self._config, 'email.host')
        self.EMAIL_PORT = glom(self._config, 'email.port')
        self.EMAIL_USER = glom(self._config, 'email.user')
        self.EMAIL_PASSWORD = glom(self._config, 'email.password')
        self.EMAIL_SEND_TO = glom(self._config, 'email.receiver')
        self.EMAIL_SSL = glom(self._config, 'email.ssl')
        self.EMAIL_SEND = glom(self._config, 'email.send')

        # 钉钉
        self.DINGDING_WEBHOOK = glom(self._config, 'dingding.webhook')
        self.DINGDING_PROXY = {
            'http': glom(self._config, 'dingding.proxies.http')
            if glom(self._config, 'dingding.proxies.http') != ''
            else None,
            'https': glom(self._config, 'dingding.proxies.https')
            if glom(self._config, 'dingding.proxies.https') != ''
            else None,
        }
        self.DINGDING_SEND = glom(self._config, 'dingding.send')

        # 飞书
        self.FEISHU_WEBHOOK = glom(self._config, 'feishu.webhook')
        self.FEISHU_PROXY = {
            'http': glom(self._config, 'feishu.proxies.http')
            if glom(self._config, 'feishu.proxies.http') != ''
            else None,
            'https': glom(self._config, 'feishu.proxies.https')
            if glom(self._config, 'feishu.proxies.https') != ''
            else None,
        }
        self.FEISHU_SEND = glom(self._config, 'feishu.send')

        # 企业微信
        self.WECHAT_WEBHOOK = glom(self._config, 'wechat.webhook')
        self.WECHAT_PROXY = {
            'http': glom(self._config, 'wechat.proxies.http')
            if glom(self._config, 'wechat.proxies.http') != ''
            else None,
            'https': glom(self._config, 'wechat.proxies.https')
            if glom(self._config, 'wechat.proxies.https') != ''
            else None,
        }
        self.WECHAT_SEND = glom(self._config, 'wechat.send')

        # 请求发送
        self.REQUEST_TIMEOUT = glom(self._config, 'request.timeout')
        self.REQUEST_VERIFY = glom(self._config, 'request.verify')
        self.REQUEST_REDIRECTS = glom(self._config, 'request.redirects')
        self.REQUEST_PROXIES_REQUESTS = {
            'http': glom(self._config, 'request.proxies.http')
            if glom(self._config, 'request.proxies.http') != ''
            else None,
            'https': glom(self._config, 'request.proxies.https')
            if glom(self._config, 'request.proxies.https') != ''
            else None,
        }
        self.REQUEST_PROXIES_HTTPX = {
            'http://': glom(self._config, 'request.proxies.http')
            if glom(self._config, 'request.proxies.http') != ''
            else None,
            'https://': glom(self._config, 'request.proxies.https')
            if glom(self._config, 'request.proxies.https') != ''
            else None,
        }
        self.REQUEST_RETRY = glom(self._config, 'request.retry')


@lru_cache(maxsize=None)
def cache_httpfpt_config() -> HttpFptConfig:
    return HttpFptConfig()


httpfpt_config = cache_httpfpt_config()
