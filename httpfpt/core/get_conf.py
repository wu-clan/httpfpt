#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functools import lru_cache
from pathlib import Path

from glom import glom

from httpfpt.common.errors import ConfigInitError
from httpfpt.common.toml_handler import read_toml

__all__ = ['httpfpt_config']


class HttpFptConfig:
    def __init__(self) -> None:
        self.settings = read_toml(str(Path(__file__).resolve().parent), 'conf.toml')
        try:
            # 项目目录名
            self.PROJECT_NAME = glom(self.settings, 'project.name')

            # 测试报告
            self.TEST_REPORT_TITLE = glom(self.settings, 'report.title')
            self.TESTER_NAME = glom(self.settings, 'report.tester_name')
            self.JENKINS_URL = glom(self.settings, 'report.jenkins_url')

            # mysql 数据库
            self.MYSQL_HOST = glom(self.settings, 'mysql.host')
            self.MYSQL_PORT = glom(self.settings, 'mysql.port')
            self.MYSQL_USER = glom(self.settings, 'mysql.user')
            self.MYSQL_PASSWORD = glom(self.settings, 'mysql.password')
            self.MYSQL_DATABASE = glom(self.settings, 'mysql.database')
            self.MYSQL_CHARSET = glom(self.settings, 'mysql.charset')

            # redis 数据库
            self.REDIS_HOST = glom(self.settings, 'redis.host')
            self.REDIS_PORT = glom(self.settings, 'redis.port')
            self.REDIS_PASSWORD = glom(self.settings, 'redis.password')
            self.REDIS_DATABASE = glom(self.settings, 'redis.database')
            self.REDIS_TIMEOUT = glom(self.settings, 'redis.timeout')

            # 邮件
            self.EMAIL_SERVER = glom(self.settings, 'email.host')
            self.EMAIL_PORT = glom(self.settings, 'email.port')
            self.EMAIL_USER = glom(self.settings, 'email.user')
            self.EMAIL_PASSWORD = glom(self.settings, 'email.password')
            self.EMAIL_SEND_TO = glom(self.settings, 'email.receiver')
            self.EMAIL_SSL = glom(self.settings, 'email.ssl')
            self.EMAIL_SEND = glom(self.settings, 'email.send')

            # 钉钉
            self.DINGDING_WEBHOOK = glom(self.settings, 'dingding.webhook')
            self.DINGDING_PROXY = {
                'http': glom(self.settings, 'dingding.proxies.http')
                if glom(self.settings, 'dingding.proxies.http') != ''
                else None,
                'https': glom(self.settings, 'dingding.proxies.https')
                if glom(self.settings, 'dingding.proxies.https') != ''
                else None,
            }
            self.DINGDING_SEND = glom(self.settings, 'dingding.send')

            # 飞书
            self.FEISHU_WEBHOOK = glom(self.settings, 'feishu.webhook')
            self.FEISHU_PROXY = {
                'http': glom(self.settings, 'feishu.proxies.http')
                if glom(self.settings, 'feishu.proxies.http') != ''
                else None,
                'https': glom(self.settings, 'feishu.proxies.https')
                if glom(self.settings, 'feishu.proxies.https') != ''
                else None,
            }
            self.FEISHU_SEND = glom(self.settings, 'feishu.send')

            # 企业微信
            self.WECHAT_WEBHOOK = glom(self.settings, 'wechat.webhook')
            self.WECHAT_PROXY = {
                'http': glom(self.settings, 'wechat.proxies.http')
                if glom(self.settings, 'wechat.proxies.http') != ''
                else None,
                'https': glom(self.settings, 'wechat.proxies.https')
                if glom(self.settings, 'wechat.proxies.https') != ''
                else None,
            }
            self.WECHAT_SEND = glom(self.settings, 'wechat.send')

            # 请求发送
            self.REQUEST_GLOBAL_ENV = glom(self.settings, 'request.global_env')
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
            raise ConfigInitError(f'配置解析失败：缺失参数 {str(e)}，请核对项目配置文件')


@lru_cache(maxsize=None)
def cache_httpfpt_config() -> HttpFptConfig:
    return HttpFptConfig()


httpfpt_config = cache_httpfpt_config()
