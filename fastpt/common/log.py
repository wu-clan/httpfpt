#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from loguru import logger


class Logger:

    @staticmethod
    def log() -> logger:
        """
        日志记录器
        :return:
        """
        # 日志存放路径
        LOG_PATH = os.path.join(os.path.abspath("."), 'log')

        if not os.path.join(LOG_PATH):
            os.makedirs(LOG_PATH)

        log_file = os.path.join(LOG_PATH, 'api_test.log')

        logger.add(
            log_file,
            level='DEBUG',
            rotation='00:00',
            retention='7 days',
            encoding='utf-8',
            enqueue=True,
            backtrace=True,
            diagnose=True,
        )

        return logger


log = Logger.log()
