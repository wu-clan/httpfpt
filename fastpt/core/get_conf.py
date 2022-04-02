#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from fastpt.common.toml_operate import read_toml

__config = read_toml(os.path.join(os.getcwd(), 'core'), 'conf.toml')

# 项目目录名
PROJECT_NAME = __config['project']['project']

# 测试人员信息
TESTER_NAME = __config['tester']['tester_name']

# 数据库
DB_HOST = __config['mysql']['host']
DB_PORT = __config['mysql']['port']
DB_USER = __config['mysql']['user']
DB_PASSWORD = __config['mysql']['password']
DB_DATABASE = __config['mysql']['database']
DB_CHARSET = __config['mysql']['charset']

# 邮件
EMAIL_HOST_SERVER = __config['email']['host_server']
EMAIL_PORT = __config['email']['port']
EMAIL_USER = __config['email']['user']
EMAIL_PASSWORD = __config['email']['password']
EMAIL_TIMEOUT = __config['email']['timeout']
EMAIL_SEND_TO = __config['email']['send_to']

# 请求发送
REQUEST_TIMEOUT = __config['request']['timeout']
REQUEST_INTERVAL = __config['request']['interval']
REQUEST_VERIFY = __config['request']['verify']
