#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
import os

from typing import TYPE_CHECKING

from loguru import logger

from httpfpt.core.path_conf import httpfpt_path_config

if TYPE_CHECKING:
    import loguru


class PropagateHandler(logging.Handler):
    def emit(self, record) -> None:  # noqa: ANN001
        logging.getLogger(record.name).handle(record)


class Logger:
    @staticmethod
    def log() -> loguru.Logger:
        """
        日志记录器

        :return:
        """
        log_path = httpfpt_path_config.log_dir

        if not os.path.join(log_path):
            os.makedirs(log_path)

        log_file = os.path.join(log_path, 'httpfpt.log')

        # 清除 logger 配置
        logger.remove()

        # 控制台输出，建议通过 pytest.ini 配置
        # logger.add(
        #     sys.stdout,
        #     format='{time:YYYYMMDD HH:mm:ss.SSS} | <level>{level: <8}</level> | <level>{message}</level>',
        # )

        # 将 logging message 替换为 loguru message
        logger.add(PropagateHandler(), format='<level>{message}</level>')

        # 输出到文件
        logger.add(
            log_file,
            format='<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>',
            level='DEBUG',
            rotation='00:00',
            retention='7 days',
            encoding='utf8',
            enqueue=True,
            backtrace=True,
            diagnose=False,
            catch=True,
        )

        return logger


log = Logger().log()
