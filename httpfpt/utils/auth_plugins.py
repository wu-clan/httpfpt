#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from jsonpath import jsonpath

from httpfpt.common.yaml_handler import read_yaml
from httpfpt.core.path_conf import AUTH_CONF_PATH
from httpfpt.db.redis_db import redis_client
from httpfpt.enums.request.auth import AuthType
from httpfpt.utils.enum_control import get_enum_values

auth_data = read_yaml(AUTH_CONF_PATH, filename='auth.yaml')
IS_AUTH = auth_data['is_auth']
AUTH_TYPE = auth_data['auth_type']


class AuthPlugins:
    def __init__(self) -> None:
        self.auth_type = AUTH_TYPE
        if not getattr(AuthType, self.auth_type, None):
            raise ValueError(f'认证类型错误, 仅允许 {get_enum_values(AuthType)} 其中之一, 请检查认证配置文件')

    @property
    def bearer_token(self) -> str:
        url = auth_data[f'{self.auth_type}']['url']
        username = auth_data[f'{self.auth_type}']['username']
        password = auth_data[f'{self.auth_type}']['password']
        headers = auth_data[f'{self.auth_type}']['headers']
        headers.update({'Connection': 'close'})
        timeout = auth_data[f'{self.auth_type}']['timeout'] or 86400
        aap_bearer_token = redis_client.redis.get(f'{redis_client.prefix}:bearer_token')
        if aap_bearer_token:
            token = aap_bearer_token
        else:
            request_data = {
                'url': url,
                'data': {'username': username, 'password': password},
                'headers': headers,
                'proxies': {'http': None, 'https': None},
            }
            if 'json' in str(headers):
                request_data.update({'json': request_data.pop('data')})
            response = requests.session().post(**request_data)
            token = jsonpath(response.json(), auth_data[f'{self.auth_type}']['token_key'])[0]
            redis_client.set(f'{redis_client.prefix}:bearer_token', token, ex=timeout)
        return token
