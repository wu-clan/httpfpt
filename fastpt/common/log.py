#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from loguru import logger


class Logger:

    def __init__(self, log_path=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))):
        self.log_path = log_path

    def log(self) -> logger:
        """
        日志记录器

        :return:
        """
        if not os.path.join(self.log_path):
            os.makedirs(self.log_path)

        log_file = os.path.join(self.log_path, 'log', 'api_test.log')

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


log = Logger().log()
