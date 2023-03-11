#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
import os

import loguru
from loguru import logger

from fastpt.core.path_conf import LOG_PATH


class Logger:

    @staticmethod
    def log() -> loguru.Logger:
        """
        日志记录器

        :return:
        """
        if not os.path.join(LOG_PATH):
            os.makedirs(LOG_PATH)

        log_file = os.path.join(LOG_PATH, 'api_test.log')

        # 清除 logger 配置
        logger.remove()

        # # 控制台输出
        # logger.add(
        #     sys.stdout,
        #     format="{time:YYYYMMDD HH:mm:ss.SSS} | <level>{level: <8}</level> | <level>{message}</level>",
        # )

        # 将 loguru 传播到 logging
        class PropagateHandler(logging.Handler):
            def emit(self, record):
                logging.getLogger(record.name).handle(record)

        logger.add(
            PropagateHandler(),
            format="| <level>{message}</level>",
            level='DEBUG'
        )

        # 输出到文件
        logger.add(
            log_file,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            level='DEBUG',
            rotation='00:00',
            retention='7 days',
            encoding='utf8',
            enqueue=True,
            backtrace=True,
            diagnose=False,
            catch=True
        )

        return logger


log = Logger().log()
