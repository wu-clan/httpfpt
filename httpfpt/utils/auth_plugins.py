#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

from functools import lru_cache

import requests

from jsonpath import findall

from httpfpt.common.errors import AuthError, SendRequestError
from httpfpt.common.yaml_handler import read_yaml
from httpfpt.core.path_conf import httpfpt_path
from httpfpt.db.redis_db import redis_client
from httpfpt.enums.request.auth import AuthType
from httpfpt.utils.enum_control import get_enum_values


class AuthPlugins:
    def __init__(self) -> None:
        self.auth_data = self.get_auth_data()
        self.is_auth = self.auth_data['is_auth']
        self.auth_type = self.auth_data['auth_type']
        self.auth_type_verify()
        self.timeout = self.auth_data[f'{self.auth_type}']['timeout'] or 86400

    @lru_cache
    def get_auth_data(self) -> dict:
        """获取授权数据"""
        auth_data = read_yaml(httpfpt_path.auth_conf_dir, filename='auth.yaml')
        return auth_data

    def auth_type_verify(self) -> None:
        """授权类型检查"""
        _allow_auth_type = get_enum_values(AuthType)
        if self.auth_type not in _allow_auth_type:
            raise AuthError(f'认证类型错误, 允许 {_allow_auth_type} 之一, 请检查认证配置文件')

    def request_auth(self) -> requests.Response:
        try:
            url = self.auth_data[f'{self.auth_type}']['url']
            username = self.auth_data[f'{self.auth_type}']['username']
            password = self.auth_data[f'{self.auth_type}']['password']
            headers = self.auth_data[f'{self.auth_type}']['headers']
            request_data = {
                'url': url,
                'data': {'username': username, 'password': password},
                'headers': headers,
                'proxies': {'http': None, 'https': None},
            }
            if 'application/json' in str(headers):
                request_data.update({'json': request_data.pop('data')})
            response = requests.post(**request_data)
            response.raise_for_status()
        except Exception as e:
            raise SendRequestError(f'授权接口请求响应异常: {e}')
        return response

    @property
    def bearer_token(self) -> str:
        cache_bearer_token = redis_client.get(f'{redis_client.token_prefix}:bearer_token', logging=False)
        if cache_bearer_token:
            token = cache_bearer_token
        else:
            res = self.request_auth()
            jp_token = findall(self.auth_data[f'{self.auth_type}']['token_key'], res.json())
            token = jp_token[0]
            if not token:
                raise AuthError('Token 获取失败，请检查登录接口响应或 token 提取表达式')
            redis_client.set(f'{redis_client.token_prefix}:bearer_token', token, ex=self.timeout)
        return token

    @property
    def bearer_token_custom(self) -> str:
        cache_bearer_token_custom = redis_client.get(f'{redis_client.token_prefix}:bearer_token_custom', logging=False)
        if cache_bearer_token_custom:
            token = cache_bearer_token_custom
        else:
            token = self.auth_data[f'{self.auth_type}']['token']
            redis_client.set(f'{redis_client.token_prefix}:bearer_token_custom', token, ex=self.timeout)
        return token

    @property
    def header_cookie(self) -> dict:
        cache_cookie = redis_client.get(f'{redis_client.cookie_prefix}:header_cookie', logging=False)
        if cache_cookie:
            cookies = json.loads(cache_cookie)
        else:
            res = self.request_auth()
            res_cookie = res.cookies
            cookies = {k: v for k, v in res_cookie.items()}
            if not cookies:
                raise AuthError('Cookie 获取失败，请检查登录接口响应')
            redis_client.set(
                f'{redis_client.cookie_prefix}:header_cookie', json.dumps(cookies, ensure_ascii=False), ex=self.timeout
            )
        return cookies


auth = AuthPlugins()
