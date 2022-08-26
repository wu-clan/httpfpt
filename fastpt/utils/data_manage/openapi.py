#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import copy
import os
import warnings
from typing import Union, Optional

import requests
import typer

from fastpt.common.json_handler import read_json_file
from fastpt.common.yaml_handler import write_yaml
from fastpt.core.get_conf import PROJECT_NAME
from fastpt.core.path_conf import YAML_DATA_PATH
from fastpt.utils.file_control import get_file_property
from fastpt.utils.time_control import get_current_timestamp


class SwaggerParser:

    def __init__(self, version: int = None, data: dict = None):
        """
        初始化参数

        :param version:
        :param data:
        """
        self.version = version
        self.data = data

    def import_openapi_to_yaml(self, openapi: str, project: Optional[str] = None):
        """
        导入 openapi 数据到 yaml

        :param openapi:
        :param project:
        :return:
        """
        global warn_operationId  # noqa
        self.get_swagger_data(openapi)
        try:
            config = {}
            config.update({
                'allure': {
                    'epic': self.data['info']['title'],
                    'feature': self.data['tags'][0]['name'] if self.data.get('tags') is not None else '未知',
                    'story': self.data['info']['description']
                },
                'request': {
                    'env': 'dev.env'
                },
                'module': self.data['info']['title']
            })
            case = {}
            tag = ''
            tag_case = {}
            root_case = {}
            for p, v in self.data['paths'].items():
                for m, vv in v.items():
                    params = self.get_test_steps_params(vv)
                    headers = self.get_test_steps_headers(vv)
                    if self.version == 2:
                        data = self.get_request_data(vv) if m.lower() != 'get' else None
                        files = self.get_request_files(vv) if m.lower() != 'get' else None
                    else:
                        try:
                            schema = vv['requestBody']['content'][headers['Content-Type']]['schema']['$ref'].split(
                                '/')[-1] if vv.get('requestBody') is not None else None
                        except KeyError:
                            schema = vv['requestBody']['content'][headers['Content-Type']]['schema']
                            warn_operationId = vv['operationId']
                        data = self.get_request_data(schema) if schema is not None else None
                        files = self.get_request_files(schema) if schema is not None else None
                    data_type = None
                    if headers is not None:
                        data_type = 'json' if 'application/json' in headers else 'data'
                    case = copy.deepcopy(case)
                    case.update({
                        'name': vv.get('summary'),
                        'case_id': vv.get('operationId'),
                        'description': vv.get('description'),
                        'is_run': vv.get('deprecated', True),
                        'request': {
                            'method': m,
                            'url': p,
                            'params': params,
                            'headers': headers,
                            'data_type': data_type,
                            'data': data,
                            'files': files
                        }
                    })
                    # 按 tag 划分目录
                    tag_ = vv.get('tags')
                    if tag_ is not None:
                        dtag = copy.deepcopy(tag)
                        tag = tag_[0]
                        if dtag != tag:
                            tag_case.update({tag: [case]})
                        else:
                            tag_case[tag].append(case)

                    else:
                        root_case = copy.deepcopy(root_case)
                        if root_case.get('root') is None:
                            root_case.update({'root': [case]})
                        else:
                            root_case[tag].append(case)
            if (len(tag_case) or len(root_case)) > 0:
                typer.secho('⏳ 奋力导入中...', fg='green', bold=True)
            # 写入项目 tag 目录
            if len(tag_case) > 0:
                for k, v in tag_case.items():
                    case_file_data = {'config': config, 'test_steps': v}
                    write_yaml(
                        YAML_DATA_PATH,
                        os.sep.join([
                            PROJECT_NAME if project is None else project,
                            k,
                            get_file_property(openapi)[1] + '.yaml' if not openapi.startswith('http') else
                            f'openapi_{k}.yaml'
                        ]),
                        case_file_data
                    )
            # 写入项目根目录
            if len(root_case) > 0:
                for _, v in tag_case.items():
                    case_file_data = {'config': config, 'test_steps': v}
                    write_yaml(
                        YAML_DATA_PATH,
                        os.sep.join([
                            PROJECT_NAME if project is None else project,
                            get_file_property(openapi)[1] + '.yaml' if not openapi.startswith('http') else
                            f'openapi_{get_current_timestamp()}.yaml'
                        ]),
                        case_file_data
                    )
        except Exception as e:
            raise e
        else:
            typer.secho('✅ 导入 openapi 数据成功')

    def get_swagger_data(self, source: str) -> None:
        """
        请求 swagger 数据

        :param source:
        :return:
        """
        if source.startswith('http'):
            request = requests.session()
            request.trust_env = False
            data = request.get(source).json()
            openapi = data.get('openapi')
            swagger = data.get('swagger')
            if not (openapi or swagger):
                raise ValueError(f"请输入正确的 openapi 地址")
        else:
            data = read_json_file(None, filename=source)
            openapi = data.get('openapi')
            swagger = data.get('swagger')
            if not (openapi or swagger):
                raise ValueError(f"获取 openapi 数据失败，请使用合法的 openapi 文件")
        if openapi is not None and int(openapi.split('.')[0]) == 3:
            self.version = 3
        elif swagger == '2.0':
            self.version = 2
        else:
            raise Exception("不受支持的 openapi 版本")
        self.data = data

    def get_test_steps_params(self, value: dict) -> Union[dict, None]:
        """
        获取查询参数

        :param value:
        :return:
        """
        data = {}
        if self.version == 2:
            params = value.get('parameters')
            if params is not None:
                for i in params:
                    if i['in'] == 'path':
                        data = {i['name']: None}
            return data if len(data) > 0 else None
        else:
            params = value.get('parameters')
            if params is not None:
                for i in params:
                    data = {i['name']: None}
            return data if len(data) > 0 else None

    def get_test_steps_headers(self, value: dict) -> Union[dict, None]:
        """
        获取查询参数

        :param value:
        :return:
        """
        data = {}
        if self.version == 2:
            headers = value.get('consumes')
            if headers is not None:
                data = {"Content-Type": headers[0]}
            return data if len(data) > 0 else None
        else:
            headers = value.get('requestBody')
            if headers is not None:
                content = headers['content']
                data = {'Content-Type': f'{[k for k in content.keys()][0]}'}
            return data if len(data) > 0 else None

    def get_schema_data(self, name: str) -> dict:
        """
        获取 schema 数据

        :param name:
        :return:
        """
        if self.version == 2:
            data = self.data.get('definitions').get(name)
        else:
            data = self.data.get('components').get('schemas').get(name)
        return data

    def get_request_data(self, value: Union[str, dict]):
        """
        获取请求 data

        :param value:
        :return:
        """
        data = {}
        if self.version == 2:
            if len(value['parameters']) > 0:
                for i in value['parameters']:
                    if i.get('type') is None:
                        data[i['name']] = self.format_value('object')  # noqa
                    else:
                        if i.get('type') != 'file':
                            data[i['name']] = self.format_value(i.get('type', 'object'))  # noqa
            return data
        else:
            if not isinstance(value, dict):
                schema_data = self.get_schema_data(value)
                for k, v in schema_data['properties'].items():
                    if v.get('format') is None:
                        data[k] = self.format_value(v.get('type', 'object'))
                    else:
                        if v.get('format') != 'binary':
                            data[k] = self.format_value(v.get('type', 'object'))
            else:
                # 请求体使用了非 schema 格式入参
                warnings.warn(f'接口(ID) {warn_operationId} 使用了非 schema 入参')
                if value.get('type') is None:
                    data[value['title']] = self.format_value('object')
                else:
                    if value.get('type') != 'file':
                        data[value['title']] = self.format_value(value.get('type', 'object'))
            return data

    def get_request_files(self, value: Union[str, dict]):
        """
        获取请求 files

        :param value:
        :return:
        """
        files = {}
        if self.version == 2:
            for v in value['parameters']:
                if v.get('type') == 'file':
                    files[v['name']] = self.format_value('object')  # noqa
            return files
        else:
            if not isinstance(value, dict):
                schema_data = self.get_schema_data(value)
                for k, v in schema_data['properties'].items():
                    if v.get('format') == 'binary':
                        files[k] = self.format_value(v.get('type', 'object'))
                return files

    @staticmethod
    def format_value(value_type: str):
        if value_type == 'string':
            v = ''
        elif value_type == 'integer':
            v = 0
        elif value_type == 'number':
            v = 0
        elif value_type == 'boolean':
            v = False
        elif value_type == 'object':
            v = {}
        elif value_type == 'array':
            v = [{}]
        elif value_type == 'arrayString':
            v = []
        else:
            raise Exception(f"存在不支持的类型：{value_type}")
        return v
