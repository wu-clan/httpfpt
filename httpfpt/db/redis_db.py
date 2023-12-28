#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any

from redis import AuthenticationError, Redis

from httpfpt.common.log import log
from httpfpt.core.get_conf import config


class RedisDB(Redis):
    def __init__(self) -> None:
        super().__init__(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            password=config.REDIS_PASSWORD,
            db=config.REDIS_DATABASE,
            socket_timeout=config.REDIS_TIMEOUT,
            decode_responses=True,  # 转码 utf-8
        )
        self.prefix = 'httpfpt'
        self.token_prefix = f'{self.prefix}:token'
        self.case_data_prefix = f'{self.prefix}:case_data'
        self.case_id_file_prefix = f'{self.prefix}:case_id_file'

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

    def get(self, name: Any, logging: bool = True) -> Any:
        """
        获取 redis 数据

        :param name:
        :param logging:
        :return:
        """
        data = super().get(name)
        if not data:
            if logging:
                log.warning(f'获取 redis 数据 {name} 失败, 此数据不存在')
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
        if super().exists(key):
            self.delete(key)
        self.set(key, value, **kwargs)

    def delete_prefix(self, prefix: str, exclude: str | None = None) -> None:
        """
        删除 redis 符合前缀的数据

        :param prefix: key 前缀
        :param exclude: 排除的前缀
        :return:
        """
        for key in self.scan_iter(match=f'{prefix}*'):
            if not exclude:
                self.delete(key)
            else:
                if not key.startswith(exclude):
                    self.delete(key)


redis_client = RedisDB()
