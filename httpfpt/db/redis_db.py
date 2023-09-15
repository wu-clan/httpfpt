#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any

from redis import Redis, AuthenticationError

from httpfpt.common.log import log
from httpfpt.core import get_conf


class RedisDB(Redis):
    def __init__(self) -> None:
        super().__init__(
            host=get_conf.REDIS_HOST,
            port=get_conf.REDIS_PORT,
            password=get_conf.REDIS_PASSWORD,
            db=get_conf.REDIS_DATABASE,
            socket_timeout=get_conf.REDIS_TIMEOUT,
            decode_responses=True,  # 转码 utf-8
        )
        self.prefix = 'httpfpt'

    def init(self) -> None:
        try:
            self.ping()
        except TimeoutError:
            log.error('数据库 redis 连接超时')
        except AuthenticationError:
            log.error('数据库 redis 授权认证错误')
        except Exception as e:
            log.error(f'数据库 redis 连接异常: {e}')
        else:
            log.info('数据库 redis 连接成功')

    def get(self, key: Any) -> Any:
        """
        获取 redis 数据

        :param key:
        :return:
        """
        data = super().get(key)
        if not data:
            log.warning(f'获取 redis 数据 {key} 失败, 此数据不存在')
        return data

    def get_prefix(self, prefix: str) -> list:
        """
        获取 redis 符合前缀的数据

        :param prefix: key 前缀
        :return:
        """
        data = []
        for key in self.scan_iter(match=f'{prefix}*'):
            value = super().get(key)
            if value:
                data.append(value)
        return data

    def rset(self, key: Any, value: Any, **kwargs) -> None:
        """
        重置设置 redis 数据

        :param key:
        :param value:
        :param kwargs:
        :return:
        """
        self.delete(key)
        self.set(key, value, **kwargs)

    def exists(self, *key: Any) -> int:
        """
        判断 redis 数据是否存在

        :param key:
        :return:
        """
        num = super().exists(*key)
        if not num:
            log.error(f'不存在 redis 数据 {key}')
        return num


redis_client = RedisDB()
