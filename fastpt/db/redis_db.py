#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any

from redis import Redis, AuthenticationError

from fastpt.common.log import log
from fastpt.core import get_conf


class RedisDB:

    def __init__(self):
        self.redis = Redis(
            host=get_conf.REDIS_HOST,
            port=get_conf.REDIS_PORT,
            password=get_conf.REDIS_PASSWORD,
            db=get_conf.REDIS_DATABASE,
            socket_timeout=get_conf.REDIS_TIMEOUT,
            decode_responses=True  # 转码 utf-8
        )

    def __call__(self, *args, **kwargs):
        try:
            self.redis.ping()
        except TimeoutError:
            log.error("数据库 redis 连接超时")
        except AuthenticationError:
            log.error("数据库 redis 授权认证错误")
        except Exception as e:
            log.error(f'数据库 redis 连接异常: {e}')

    def get(self, key: Any):
        """
        获取 redis 数据

        :param key:
        :return:
        """
        return self.redis.get(key)
