#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import os.path

from httpfpt.common.errors import ConfigInitError

__all__ = [
    'httpfpt_config',
    'set_httpfpt_config',
]

# global config
httpfpt_config = None


class HttpFptConfig:
    def __init__(self, settings: dict) -> None:
        """
        项目配置初始化

        :param settings:
        """
        try:
            # 项目目录名
            self.PROJECT_NAME = settings['project']['project']
            # 测试报告
            self.TEST_REPORT_TITLE = settings['report']['title']
            self.TESTER_NAME = settings['report']['tester_name']
            # mysql 数据库
            self.MYSQL_HOST = settings['mysql']['host']
            self.MYSQL_PORT = settings['mysql']['port']
            self.MYSQL_USER = settings['mysql']['user']
            self.MYSQL_PASSWORD = settings['mysql']['password']
            self.MYSQL_DATABASE = settings['mysql']['database']
            self.MYSQL_CHARSET = settings['mysql']['charset']
            # redis 数据库
            self.REDIS_HOST = settings['redis']['host']
            self.REDIS_PORT = settings['redis']['port']
            self.REDIS_PASSWORD = settings['redis']['password']
            self.REDIS_DATABASE = settings['redis']['database']
            self.REDIS_TIMEOUT = settings['redis']['timeout']
            # 邮件
            self.EMAIL_SERVER = settings['email']['host_server']
            self.EMAIL_PORT = settings['email']['port']
            self.EMAIL_USER = settings['email']['user']
            self.EMAIL_PASSWORD = settings['email']['password']
            self.EMAIL_SEND_TO = settings['email']['send_to']
            self.EMAIL_SSL = settings['email']['ssl']
            self.EMAIL_REPORT_SEND = settings['email']['send_report']
            # 钉钉
            self.DING_TALK_WEBHOOK = settings['ding_talk']['webhook']
            self.DING_TALK_PROXY = {
                'http': settings['ding_talk']['proxies']['http']
                if settings['ding_talk']['proxies']['http'] != ''
                else None,
                'https': settings['ding_talk']['proxies']['https']
                if settings['ding_talk']['proxies']['https'] != ''
                else None,
            }
            self.DING_TALK_REPORT_SEND = settings['ding_talk']['send_report']
            # 飞书
            self.LARK_TALK_WEBHOOK = settings['lark_talk']['webhook']
            self.LARK_TALK_PROXY = {
                'http': settings['lark_talk']['proxies']['http']
                if settings['lark_talk']['proxies']['http'] != ''
                else None,
                'https': settings['lark_talk']['proxies']['https']
                if settings['lark_talk']['proxies']['https'] != ''
                else None,
            }
            self.LARK_TALK_REPORT_SEND = settings['lark_talk']['send_report']
            # 请求发送
            self.REQUEST_TIMEOUT = settings['request']['timeout']
            self.REQUEST_VERIFY = settings['request']['verify']
            self.REQUEST_REDIRECTS = settings['request']['redirects']
            self.REQUEST_PROXIES_REQUESTS = {
                'http': settings['request']['proxies']['http']
                if settings['request']['proxies']['http'] != ''
                else None,
                'https': settings['request']['proxies']['https']
                if settings['request']['proxies']['https'] != ''
                else None,
            }
            self.REQUEST_PROXIES_HTTPX = {
                'http://': settings['request']['proxies']['http']
                if settings['request']['proxies']['http'] != ''
                else None,
                'https://': settings['request']['proxies']['https']
                if settings['request']['proxies']['https'] != ''
                else None,
            }
            self.REQUEST_RETRY = settings['request']['retry']
        except KeyError as e:
            raise ConfigInitError(
                f'配置文件解析失败：缺失参数 "{str(e)}"，请核对配置文件或字典，若尚未配置，可通过'
                f'set_project_config() 设置项目配置，或将 HTTPFPT_PROJECT_CONFIG 环境变量指向配置文件路径'
            )


def set_httpfpt_config(settings: str | dict, config_filename: str | None = None) -> HttpFptConfig:
    """
    设置项目配置

    :param settings: 项目配置，字典或指定 toml 配置文件
    :param config_filename:
    :return:
    """
    global httpfpt_config

    if isinstance(settings, str):
        from httpfpt.common.toml_handler import read_toml

        if not os.path.isdir(settings) and not os.path.isfile(settings):
            raise ConfigInitError('运行失败，')
        conf = read_toml(settings, config_filename)
    else:
        conf = settings

    httpfpt_config = HttpFptConfig(conf)
    return httpfpt_config
