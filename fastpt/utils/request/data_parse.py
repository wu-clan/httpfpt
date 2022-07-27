#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from typing import Union

import allure
from _pytest.outcomes import Skipped

from fastpt.common.log import log
from fastpt.utils.request.vars_extract import VarsExtractor


class DataParse:

    def __init__(self, request_data: dict):
        self.request_data = request_data
        self.skip()  # put down

    @property
    def module(self) -> str:
        module = self.request_data['module']
        return module

    @property
    def case_id(self) -> str:
        case_id = self.request_data['case_id']
        return case_id

    @property
    def case_desc(self) -> Union[str, None]:
        case_desc = self.request_data['case_desc']
        return case_desc

    def skip(self):
        skip = self.request_data['is_run']
        if skip is not None:
            if not skip or str(skip).lower() == 'false':
                allure.dynamic.title(
                    f"用例 module: {self.module};"
                    f"用例 case_id: {self.case_id}"
                )
                log.warning('此用例已设置跳过')
                raise Skipped('此用例已设置跳过')

    @property
    def method(self) -> str:
        return self.request_data['method']

    @property
    def url(self) -> str:
        env = self.request_data['env']
        url = self.request_data['url']
        if env is not None:
            host = VarsExtractor().vars_replace(env)
            url = host + url
        return url

    @property
    def params(self) -> Union[dict, bytes, None]:
        params = self.request_data['params']
        if params is not None:
            params = VarsExtractor().vars_replace(params)
            if isinstance(params, str):
                params = eval(params)
        return params

    @property
    def headers(self) -> Union[dict, None]:
        headers = self.request_data['headers']
        if headers is not None:
            headers = VarsExtractor().vars_replace(headers)
            if isinstance(headers, str):
                headers = eval(headers)
            else:
                if not isinstance(headers, dict):
                    raise ValueError('参数 headers 格式错误, 必须为 dict')
        return headers

    @property
    def data_type(self) -> Union[str, None]:
        data_type = self.request_data['data_type']
        if isinstance(data_type, str):
            data_type = data_type.lower()
        return data_type

    @property
    def data(self):
        data = self.request_data['data']
        if data is not None:
            data = VarsExtractor().vars_replace(data)
            if isinstance(data, str):
                data = eval(data)
            if self.data_type == 'json':
                try:
                    data = json.dumps(data, ensure_ascii=False)
                except Exception as e:
                    raise ValueError('data 参数不是有效的 json')
        return data

    @property
    def files(self) -> Union[dict, list, None]:
        files = self.request_data['files']
        if files is not None:
            if isinstance(files, str):
                files = eval(files)
            if not isinstance(files, (list, dict)):
                raise ValueError('参数 files 格式错误, 可能由于路径中包含转义符而引起')
            for k, v in files.items():
                # 多文件
                if isinstance(v, list):
                    files = [(f'{k}', open(_, 'rb')) for _ in v]
                # 单文件
                else:
                    files = {f'{k}': open(v, "rb")}
        return files

    @property
    def files_no_parse(self) -> Union[dict, None]:
        files = self.request_data['files']
        if files is not None:
            if isinstance(files, str):
                files = eval(files)
            else:
                if not isinstance(files, (list, dict)):
                    raise ValueError('参数 files 格式错误, 可能由于路径中包含转义符而引起')
        return files

    @property
    def sql(self) -> Union[list, None]:
        sql = self.request_data['sql']
        if sql is not None:
            sql = VarsExtractor().vars_replace(sql)
            if isinstance(sql, str):
                sql = eval(sql)
            else:
                if not isinstance(sql, list):
                    raise ValueError('请求参数 sql 类型错误, 请使用 list 类型表达语句')
        return sql

    @property
    def assert_text(self) -> Union[str, list, dict, None]:
        assert_text = self.request_data['assert']
        if assert_text is not None:
            assert_text = VarsExtractor().vars_replace(assert_text)
            if isinstance(assert_text, str):
                # 单条 code 断言时, 跳过处理
                if not assert_text.startswith('assert'):
                    assert_text = eval(assert_text)
            else:
                if not isinstance(assert_text, list):
                    if not isinstance(assert_text, dict):
                        raise ValueError('请求参数 assert 类型错误, 请检查')
        return assert_text

    @property
    def get_request_args_parsed(self) -> dict:
        """
        获取解析后的请求参数

        :return:
        """
        if self.data_type != 'json':
            parsed_data = {
                'method': self.method,
                'url': self.url,
                'params': self.params,
                'headers': self.headers,
                'data': self.data,
                'files': self.files
            }
        else:
            parsed_data = {
                'method': self.method,
                'url': self.url,
                'params': self.params,
                'headers': self.headers,
                'json': self.data,
                'files': self.files
            }
        return parsed_data
