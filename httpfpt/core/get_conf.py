#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path

from httpfpt.common.toml_handler import read_toml

__config = read_toml(str(Path(__file__).resolve().parent), 'conf.toml')

# 项目目录名
PROJECT_NAME = __config['project']['project']

# 测试报告
TEST_REPORT_TITLE = __config['report']['title']
TESTER_NAME = __config['report']['tester_name']

# mysql 数据库
MysqlDB_HOST = __config['mysql']['host']
MysqlDB_PORT = __config['mysql']['port']
MysqlDB_USER = __config['mysql']['user']
MysqlDB_PASSWORD = __config['mysql']['password']
MysqlDB_DATABASE = __config['mysql']['database']

# redis 数据库
REDIS_HOST = __config['redis']['host']
REDIS_PORT = __config['redis']['port']
REDIS_PASSWORD = __config['redis']['password']
REDIS_DATABASE = __config['redis']['database']
REDIS_TIMEOUT = __config['redis']['timeout']

# 邮件
EMAIL_SERVER = __config['email']['host_server']
EMAIL_PORT = __config['email']['port']
EMAIL_USER = __config['email']['user']
EMAIL_PASSWORD = __config['email']['password']
EMAIL_SEND_TO = __config['email']['send_to']
EMAIL_SSL = __config['email']['is_ssl']
EMAIL_REPORT_SEND = __config['email']['is_send_report']

# 钉钉
DING_TALK_WEBHOOK = __config['ding_talk']['webhook']
DING_TALK_PROXY = {
    'http': __config['ding_talk']['proxies']['http'] if __config['ding_talk']['proxies']['http'] != '' else None,
    'https': __config['ding_talk']['proxies']['https'] if __config['ding_talk']['proxies']['https'] != '' else None,
}
DING_TALK_REPORT_SEND = __config['ding_talk']['is_send_report']

# 飞书
LARK_TALK_WEBHOOK = __config['lark_talk']['webhook']
LARK_TALK_PROXY = {
    'http': __config['lark_talk']['proxies']['http'] if __config['lark_talk']['proxies']['http'] != '' else None,
    'https': __config['lark_talk']['proxies']['https'] if __config['lark_talk']['proxies']['https'] != '' else None,
}
LARK_TALK_REPORT_SEND = __config['lark_talk']['is_send_report']

# 请求发送
REQUEST_TIMEOUT = __config['request']['timeout']
REQUEST_VERIFY = __config['request']['verify']
REQUEST_REDIRECTS = __config['request']['redirects']
REQUEST_PROXIES_REQUESTS = {
    'http': __config['request']['proxies']['http'] if __config['request']['proxies']['http'] != '' else None,
    'https': __config['request']['proxies']['https'] if __config['request']['proxies']['https'] != '' else None,
}
REQUEST_PROXIES_HTTPX = {
    'http://': __config['request']['proxies']['http'] if __config['request']['proxies']['http'] != '' else None,
    'https://': __config['request']['proxies']['https'] if __config['request']['proxies']['https'] != '' else None,
}
