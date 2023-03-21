#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from typing import Any, NoReturn

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

    def init(self):
        try:
            self.redis.ping()
        except TimeoutError:
            log.error("❌ 数据库 redis 连接超时")
            sys.exit(1)
        except AuthenticationError:
            log.error("❌ 数据库 redis 授权认证错误")
            sys.exit(1)
        except Exception as e:
            log.error(f'❌ 数据库 redis 连接异常: {e}')
            sys.exit(1)
        else:
            log.info("✅ 数据库 redis 连接成功")

    def get(self, key: Any) -> Any:
        """
        获取 redis 数据

        :param key:
        :return:
        """
        data = self.redis.get(key)
        if data:
            log.info(f'获取 redis 数据 {key} 成功')
        else:
            log.warning(f'获取 redis 数据 {key} 失败, 此数据不存在')
        return data

    def set(self, key: Any, value: Any, **kwargs) -> NoReturn:
        """
        设置 redis 数据

        :param key:
        :param value:
        :return:
        """
        self.redis.set(key, value, **kwargs)
        log.info(f'设置 redis 数据 {key} 成功')

    def rset(self, key: Any, value: Any, **kwargs) -> NoReturn:
        """
        重置设置 redis 数据

        :param key:
        :param value:
        :param kwargs:
        :return:
        """
        self.redis.delete(key)
        self.redis.set(key, value, **kwargs)
        log.info(f'重置 redis 数据 {key} 成功')

    def delete(self, *key: Any) -> NoReturn:
        """
        删除 redis 数据

        :param key:
        :return:
        """
        count = self.redis.delete(*key)
        if count > 0:
            log.info(f'删除 redis 数据 {key} 成功')

    def exists(self, *key: Any) -> int:
        """
        判断 redis 数据是否存在

        :param key:
        :return:
        """
        num = self.redis.exists(*key)
        if num:
            log.info(f'判断 redis 数据 {key} 存在')
        else:
            log.warning(f'判断 redis 数据 {key} 不存在')
        return num

    def lpush(self, key: Any, *value: Any) -> NoReturn:
        """
        从左侧插入列表数据

        :param key:
        :param value:
        :return:
        """
        self.redis.lpush(key, *value)
        log.info(f'从左侧插入 redis 数据 {key} 成功')

    def relpush(self, key: Any, *value: Any) -> NoReturn:
        """
        删除原数据并重新从左侧插入列表数据

        :param key:
        :param value:
        :return:
        """
        self.redis.delete(key)
        self.redis.rpush(key, *value)
        log.info(f'删除原数据并重新从左侧插入 redis 数据 {key} 成功')
