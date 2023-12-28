#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functools import lru_cache

import requests

from jsonpath import findall

from httpfpt.common.errors import AuthError
from httpfpt.common.yaml_handler import read_yaml
from httpfpt.core.path_conf import AUTH_CONF_PATH
from httpfpt.db.redis_db import redis_client
from httpfpt.enums.request.auth import AuthType
from httpfpt.utils.enum_control import get_enum_values


class AuthPlugins:
    def __init__(self) -> None:
        self.auth_data = self.get_auth_data()
        self.is_auth = self.auth_data['is_auth']
        self.auth_type = self.auth_data['auth_type']
        if not getattr(AuthType, self.auth_type, None):
            raise AuthError(f'认证类型错误, 允许 {get_enum_values(AuthType)} 之一, 请检查认证配置文件')

    @lru_cache
    def get_auth_data(self) -> dict:
        auth_data = read_yaml(AUTH_CONF_PATH, filename='auth.yaml')
        return auth_data

    @property
    def bearer_token(self) -> str:
        url = self.auth_data[f'{self.auth_type}']['url']
        username = self.auth_data[f'{self.auth_type}']['username']
        password = self.auth_data[f'{self.auth_type}']['password']
        headers = self.auth_data[f'{self.auth_type}']['headers']
        headers.update({'Connection': 'close'})
        timeout = self.auth_data[f'{self.auth_type}']['timeout'] or 86400
        cache_bearer_token = redis_client.get(f'{redis_client.token_prefix}:{url}', logging=False)
        if cache_bearer_token:
            token = cache_bearer_token
        else:
            request_data = {
                'url': url,
                'data': {'username': username, 'password': password},
                'headers': headers,
                'proxies': {'http': None, 'https': None},
            }
            if 'application/json' in str(headers):
                request_data.update({'json': request_data.pop('data')})
            response = requests.post(**request_data)
            jp_token = findall(self.auth_data[f'{self.auth_type}']['token_key'], response.json())
            token = jp_token[0]
            if not token:
                raise AuthError('Token 获取失败，请检查登录接口响应或 token_key 表达式')
            redis_client.set(f'{redis_client.token_prefix}:{url}', token, ex=timeout)
        return token
