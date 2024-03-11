#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functools import lru_cache
from pathlib import Path

from glom import glom

from httpfpt.common.toml_handler import read_toml


class Config:
    def __init__(self) -> None:
        self.__config = read_toml(str(Path(__file__).resolve().parent), 'conf.toml')

        # 项目目录名
        self.PROJECT_NAME = glom(self.__config, 'project.name')

        # 测试报告
        self.TEST_REPORT_TITLE = glom(self.__config, 'report.title')
        self.TESTER_NAME = glom(self.__config, 'report.tester_name')

        # mysql 数据库
        self.MYSQL_HOST = glom(self.__config, 'mysql.host')
        self.MYSQL_PORT = glom(self.__config, 'mysql.port')
        self.MYSQL_USER = glom(self.__config, 'mysql.user')
        self.MYSQL_PASSWORD = glom(self.__config, 'mysql.password')
        self.MYSQL_DATABASE = glom(self.__config, 'mysql.database')
        self.MYSQL_CHARSET = glom(self.__config, 'mysql.charset')

        # redis 数据库
        self.REDIS_HOST = glom(self.__config, 'redis.host')
        self.REDIS_PORT = glom(self.__config, 'redis.port')
        self.REDIS_PASSWORD = glom(self.__config, 'redis.password')
        self.REDIS_DATABASE = glom(self.__config, 'redis.database')
        self.REDIS_TIMEOUT = glom(self.__config, 'redis.timeout')

        # 邮件
        self.EMAIL_SERVER = glom(self.__config, 'email.host')
        self.EMAIL_PORT = glom(self.__config, 'email.port')
        self.EMAIL_USER = glom(self.__config, 'email.user')
        self.EMAIL_PASSWORD = glom(self.__config, 'email.password')
        self.EMAIL_SEND_TO = glom(self.__config, 'email.receiver')
        self.EMAIL_SSL = glom(self.__config, 'email.ssl')
        self.EMAIL_SEND = glom(self.__config, 'email.send')

        # 钉钉
        self.DINGDING_WEBHOOK = glom(self.__config, 'dingding.webhook')
        self.DINGDING_PROXY = {
            'http': glom(self.__config, 'dingding.proxies.http')
            if glom(self.__config, 'dingding.proxies.http') != ''
            else None,
            'https': glom(self.__config, 'dingding.proxies.https')
            if glom(self.__config, 'dingding.proxies.https') != ''
            else None,
        }
        self.DINGDING_SEND = glom(self.__config, 'dingding.send')

        # 飞书
        self.FEISHU_WEBHOOK = glom(self.__config, 'feishu.webhook')
        self.FEISHU_PROXY = {
            'http': glom(self.__config, 'feishu.proxies.http')
            if glom(self.__config, 'feishu.proxies.http') != ''
            else None,
            'https': glom(self.__config, 'feishu.proxies.https')
            if glom(self.__config, 'feishu.proxies.https') != ''
            else None,
        }
        self.FEISHU_SEND = glom(self.__config, 'feishu.send')

        # 企业微信
        self.WECHAT_TALK_WEBHOOK = glom(self.__config, 'wechat_talk.webhook')
        self.WECHAT_TALK_PROXY = {
            'http': glom(self.__config, 'wechat_talk.proxies.http')
            if glom(self.__config, 'wechat_talk.proxies.http') != ''
            else None,
            'https': glom(self.__config, 'wechat_talk.proxies.https')
            if glom(self.__config, 'wechat_talk.proxies.https') != ''
            else None,
        }
        self.WECHAT_TALK_REPORT_SEND = glom(self.__config, 'wechat_talk.send_report')

        # 请求发送
        self.REQUEST_TIMEOUT = glom(self.__config, 'request.timeout')
        self.REQUEST_VERIFY = glom(self.__config, 'request.verify')
        self.REQUEST_REDIRECTS = glom(self.__config, 'request.redirects')
        self.REQUEST_PROXIES_REQUESTS = {
            'http': glom(self.__config, 'request.proxies.http')
            if glom(self.__config, 'request.proxies.http') != ''
            else None,
            'https': glom(self.__config, 'request.proxies.https')
            if glom(self.__config, 'request.proxies.https') != ''
            else None,
        }
        self.REQUEST_PROXIES_HTTPX = {
            'http://': glom(self.__config, 'request.proxies.http')
            if glom(self.__config, 'request.proxies.http') != ''
            else None,
            'https://': glom(self.__config, 'request.proxies.https')
            if glom(self.__config, 'request.proxies.https') != ''
            else None,
        }
        self.REQUEST_RETRY = glom(self.__config, 'request.retry')


@lru_cache(maxsize=None)
def cache_config() -> Config:
    return Config()


config = cache_config()
