#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path

from fastpt.common.toml_operate import read_toml

__config = read_toml(str(Path(__file__).resolve().parent), 'conf.toml')

# 项目目录名
PROJECT_NAME = __config['project']['project']

# 测试报告
TESTER_NAME = __config['report']['tester_name']

# html 测试报告
HTML_REPORT_TITLE = __config['report']['html']['title']

# 数据库
DB_HOST = __config['mysql']['host']
DB_PORT = __config['mysql']['port']
DB_USER = __config['mysql']['user']
DB_PASSWORD = __config['mysql']['password']
DB_DATABASE = __config['mysql']['database']

# 邮件
EMAIL_SERVER = __config['email']['host_server']
EMAIL_PORT = __config['email']['port']
EMAIL_USER = __config['email']['user']
EMAIL_PASSWORD = __config['email']['password']
EMAIL_SEND_TO = __config['email']['send_to']
EMAIL_SSL = __config['email']['is_ssl']

# 请求发送
REQUEST_TIMEOUT = __config['request']['timeout']
REQUEST_INTERVAL = __config['request']['interval']
REQUEST_VERIFY = __config['request']['verify']
REQUEST_PROXIES_REQUESTS = {
    'http': __config['request']['proxies']['http'] if __config['request']['proxies']['http'] != '' else None,
    'https': __config['request']['proxies']['https'] if __config['request']['proxies']['https'] != '' else None
}
REQUEST_PROXIES_HTTPX = {
    'http://': __config['request']['proxies']['http'] if __config['request']['proxies']['http'] != '' else None,
    'https://': __config['request']['proxies']['https'] if __config['request']['proxies']['https'] != '' else None
}
