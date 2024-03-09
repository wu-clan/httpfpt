#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functools import lru_cache
from pathlib import Path

from httpfpt.common.toml_handler import read_toml


class Config:
    def __init__(self) -> None:
        self.__config = read_toml(str(Path(__file__).resolve().parent), 'conf.toml')

        # 项目目录名
        self.PROJECT_NAME = self.__config['project']['name']

        # 测试报告
        self.TEST_REPORT_TITLE = self.__config['report']['title']
        self.TESTER_NAME = self.__config['report']['tester_name']

        # mysql 数据库
        self.MYSQL_HOST = self.__config['mysql']['host']
        self.MYSQL_PORT = self.__config['mysql']['port']
        self.MYSQL_USER = self.__config['mysql']['user']
        self.MYSQL_PASSWORD = self.__config['mysql']['password']
        self.MYSQL_DATABASE = self.__config['mysql']['database']
        self.MYSQL_CHARSET = self.__config['mysql']['charset']

        # redis 数据库
        self.REDIS_HOST = self.__config['redis']['host']
        self.REDIS_PORT = self.__config['redis']['port']
        self.REDIS_PASSWORD = self.__config['redis']['password']
        self.REDIS_DATABASE = self.__config['redis']['database']
        self.REDIS_TIMEOUT = self.__config['redis']['timeout']

        # 邮件
        self.EMAIL_SERVER = self.__config['email']['host']
        self.EMAIL_PORT = self.__config['email']['port']
        self.EMAIL_USER = self.__config['email']['user']
        self.EMAIL_PASSWORD = self.__config['email']['password']
        self.EMAIL_SEND_TO = self.__config['email']['receiver']
        self.EMAIL_SSL = self.__config['email']['ssl']
        self.EMAIL_SEND = self.__config['email']['send']

        # 钉钉
        self.DINGDING_WEBHOOK = self.__config['dingding']['webhook']
        self.DINGDING_PROXY = {
            'http': self.__config['dingding']['proxies']['http']
            if self.__config['dingding']['proxies']['http'] != ''
            else None,
            'https': self.__config['dingding']['proxies']['https']
            if self.__config['dingding']['proxies']['https'] != ''
            else None,
        }
        self.DINGDING_SEND = self.__config['dingding']['send']

        # 飞书
        self.FEISHU_WEBHOOK = self.__config['feishu']['webhook']
        self.FEISHU_PROXY = {
            'http': self.__config['feishu']['proxies']['http']
            if self.__config['feishu']['proxies']['http'] != ''
            else None,
            'https': self.__config['feishu']['proxies']['https']
            if self.__config['feishu']['proxies']['https'] != ''
            else None,
        }
        self.FEISHU_SEND = self.__config['feishu']['send']

        # 请求发送
        self.REQUEST_TIMEOUT = self.__config['request']['timeout']
        self.REQUEST_VERIFY = self.__config['request']['verify']
        self.REQUEST_REDIRECTS = self.__config['request']['redirects']
        self.REQUEST_PROXIES_REQUESTS = {
            'http': self.__config['request']['proxies']['http']
            if self.__config['request']['proxies']['http'] != ''
            else None,
            'https': self.__config['request']['proxies']['https']
            if self.__config['request']['proxies']['https'] != ''
            else None,
        }
        self.REQUEST_PROXIES_HTTPX = {
            'http://': self.__config['request']['proxies']['http']
            if self.__config['request']['proxies']['http'] != ''
            else None,
            'https://': self.__config['request']['proxies']['https']
            if self.__config['request']['proxies']['https'] != ''
            else None,
        }
        self.REQUEST_RETRY = self.__config['request']['retry']


@lru_cache(maxsize=None)
def cache_config() -> Config:
    return Config()


config = cache_config()
