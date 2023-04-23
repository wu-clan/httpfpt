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
from fastpt.utils.data_manage.base_format import format_value
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

    def import_openapi_to_yaml(self, openapi_source: str, project: Optional[str] = None):
        """
        导入 openapi 数据到 yaml

        :param openapi_source:
        :param project:
        :return:
        """
        global warn_operationId  # noqa
        self.get_swagger_data(openapi_source)
        try:
            # 测试用例数据配置项
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

            # 测试用例数据
            case = {}
            # 子目录
            tag = ''
            # 子目录测试用例数据
            tag_case = {}
            # 根目录测试用例数据
            root_case = {}

            is_tag = typer.confirm('是否按openapi标签划分数据存放目录?', default=True)
            for url, values in self.data['paths'].items():
                for method, values_map in values.items():
                    params = self.get_swagger_params(values_map)
                    headers = self.get_swagger_headers(values_map)
                    if self.version == 2:
                        data = self.get_swagger_request_data(values_map) if method.lower() != 'get' else None
                        files = self.get_swagger_request_files(values_map) if method.lower() != 'get' else None
                    else:
                        try:
                            schema = \
                                values_map['requestBody']['content'][headers['Content-Type']]['schema']['$ref'].split(
                                    '/')[-1] if values_map.get('requestBody') is not None else None
                        except KeyError:
                            schema = values_map['requestBody']['content'][headers['Content-Type']]['schema']
                            warn_operationId = values_map['operationId']
                        data = self.get_swagger_request_data(schema) if schema is not None else None
                        files = self.get_swagger_request_files(schema) if schema is not None else None
                    data_type = None
                    if headers is not None:
                        data_type = 'json' if 'application/json' in headers else 'data'
                    case = copy.deepcopy(case)
                    case.update({
                        'name': values_map.get('summary'),
                        'case_id': values_map.get('operationId'),
                        'description': values_map.get('description'),
                        'is_run': values_map.get('deprecated', True),
                        'request': {
                            'method': method,
                            'url': url,
                            'params': params,
                            'headers': headers,
                            'data_type': data_type,
                            'data': data,
                            'files': files
                        }
                    })
                    tags = values_map.get('tags')
                    # 按 tag 划分目录
                    if is_tag:
                        if tags is not None:
                            dp_tag = copy.deepcopy(tag)
                            tag = tags[0]
                            tag_case.update({tag: [case]}) if dp_tag != tag else tag_case[tag].append(case)
                        else:
                            root_case = copy.deepcopy(root_case)
                            root_case.update({'root': [case]}) if root_case.get('root') is None else root_case[
                                'root'].append(case)
                    # 不按 tag 划分目录
                    else:
                        if tags:
                            dp_tag = copy.deepcopy(tag)
                            tag = tags[0]
                            root_case.update({tag: [case]}) if dp_tag != tag else root_case[tag].append(case)
                        else:
                            root_case = copy.deepcopy(root_case)
                            root_case.update({'root': [case]}) if root_case.get('root') is None else root_case[
                                'root'].append(case)
            if len(tag_case) > 0 or len(root_case) > 0:
                # 文件创建提醒
                file_list = []
                if len(tag_case) > 0:
                    for k, v in tag_case.items():
                        tag_filename = os.sep.join([
                            project or PROJECT_NAME,
                            k,
                            get_file_property(openapi_source)[1] + '.yaml' if not openapi_source.startswith('http') else
                            f'openapi_{k}.yaml'
                        ])
                        file_list.append(tag_filename)
                if len(root_case) > 0:
                    for k, v in root_case.items():
                        if k == 'root':
                            root_filename = os.sep.join([
                                project or PROJECT_NAME,
                                get_file_property(openapi_source)[1] + '.yaml' if not openapi_source.startswith(
                                    'http') else f'openapi_{get_current_timestamp()}.yaml'
                            ])
                        else:
                            root_filename = os.sep.join([
                                project or PROJECT_NAME,
                                get_file_property(openapi_source)[1] + '.yaml' if not openapi_source.startswith(
                                    'http') else f'openapi_{k}.yaml'
                            ])
                        file_list.append(root_filename)
                typer.secho('⚠️ 即将创建以下数据文件:', fg='yellow', bold=True)
                for i in file_list:
                    typer.secho(f'{i}', fg='cyan', bold=True)
                is_force_write = typer.confirm(
                    text='请检查是否存在同名文件, 此操作将强制覆盖写入所有数据文件, 是否继续执行? (此操作不可逆)',
                    default=False
                )
                # 强制写入
                if is_force_write:
                    typer.secho('⏳ 奋力导入中...', fg='green', bold=True)
                    # 写入项目 tag 目录
                    if len(tag_case) > 0:
                        for k, v in tag_case.items():
                            config['allure']['feature'] = config['module'] = k
                            case_file_data = {'config': config, 'test_steps': v}
                            write_yaml(
                                YAML_DATA_PATH,
                                os.sep.join([
                                    project or PROJECT_NAME,
                                    k,
                                    get_file_property(openapi_source)[1] + '.yaml' if not openapi_source.startswith(
                                        'http') else f'openapi_{k}.yaml'
                                ])
                                ,
                                case_file_data,
                                mode='w'
                            )
                    # 写入项目根目录
                    if len(root_case) > 0:
                        for k, v in root_case.items():
                            if k == 'root':
                                filename = get_file_property(openapi_source)[
                                               1] + '.yaml' if not openapi_source.startswith(
                                    'http') else f'openapi_{get_current_timestamp()}.yaml'
                            else:
                                filename = get_file_property(openapi_source)[
                                               1] + '.yaml' if not openapi_source.startswith(
                                    'http') else f'openapi_{k}.yaml'
                            case_file_data = {'config': config, 'test_steps': v}
                            write_yaml(
                                YAML_DATA_PATH,
                                os.sep.join([
                                    project or PROJECT_NAME,
                                    filename
                                ]),
                                case_file_data,
                                mode='w'
                            )
                # 选择写入
                else:
                    typer.secho('⚠️ 已取消强制覆写入所有数据文件', fg='yellow', bold=True)
                    is_next = typer.confirm('是否进行逐一选择创建数据文件吗?', abort=True)
                    if is_next:
                        # 写入项目 tag 目录
                        if len(tag_case) > 0:
                            for k, v in tag_case.items():
                                config['allure']['feature'] = config['module'] = k
                                case_file_data = {'config': config, 'test_steps': v}
                                tag_filename = os.sep.join([
                                    project or PROJECT_NAME,
                                    k,
                                    get_file_property(openapi_source)[1] + '.yaml' if not openapi_source.startswith(
                                        'http') else f'openapi_{k}.yaml'
                                ])
                                is_write = typer.confirm(text=f'是否需要创建 {tag_filename} 数据文件?', default=True)
                                if is_write:
                                    write_yaml(YAML_DATA_PATH, tag_filename, case_file_data, mode='w')
                        # 写入项目根目录
                        if len(root_case) > 0:
                            for k, v in root_case.items():
                                if k == 'root':
                                    root_filename = get_file_property(openapi_source)[
                                                        1] + '.yaml' if not openapi_source.startswith(
                                        'http') else f'openapi_{get_current_timestamp()}.yaml'
                                else:
                                    root_filename = get_file_property(openapi_source)[
                                                        1] + '.yaml' if not openapi_source.startswith(
                                        'http') else f'openapi_{k}.yaml'
                                is_write = typer.confirm(text=f'是否需要创建 {root_filename} 数据文件?', default=True)
                                if is_write:
                                    case_file_data = {'config': config, 'test_steps': v}
                                    write_yaml(
                                        YAML_DATA_PATH,
                                        os.sep.join([
                                            project or PROJECT_NAME,
                                            root_filename
                                        ]),
                                        case_file_data,
                                        mode='w'
                                    )
        except Exception as e:
            raise e
        else:
            typer.secho('✅ 导入 openapi 数据成功', fg='green', bold=True)

    def get_swagger_data(self, openapi_source: str) -> None:
        """
        请求 swagger 数据

        :param openapi_source:
        :return:
        """
        if openapi_source.startswith('http'):
            request = requests.session()
            request.trust_env = False
            data = request.get(openapi_source).json()
            openapi = data.get('openapi')
            swagger = data.get('swagger')
            if not (openapi or swagger):
                raise ValueError("请输入正确的 openapi 地址")
        else:
            data = read_json_file(None, filename=openapi_source)
            openapi = data.get('openapi')
            swagger = data.get('swagger')
            if not (openapi or swagger):
                raise ValueError("获取 openapi 数据失败，请使用合法的 openapi 文件")
        if openapi is not None and int(openapi.split('.')[0]) == 3:
            self.version = 3
        elif swagger == '2.0':
            self.version = 2
        else:
            raise Exception("不受支持的 openapi 版本")
        self.data = data

    def get_swagger_params(self, value: dict) -> Union[dict, None]:
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

    def get_swagger_headers(self, value: dict) -> Union[dict, None]:
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

    def get_swagger_schema_data(self, name: str) -> dict:
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

    def get_swagger_request_data(self, value: Union[str, dict]) -> Union[dict, None]:
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
            return data if len(data) > 0 else None
        else:
            if not isinstance(value, dict):
                schema_data = self.get_swagger_schema_data(value)
                for k, v in schema_data['properties'].items():
                    if v.get('format') is None:
                        data[k] = format_value(v.get('type', 'object'))
                    else:
                        if v.get('format') != 'binary':
                            data[k] = format_value(v.get('type', 'object'))
            else:
                # 请求体使用了非 schema 格式入参
                warnings.warn(f'接口(ID) {warn_operationId} 使用了非 schema 入参')
                if value.get('type') is None:
                    data[value['title']] = format_value('object')
                else:
                    if value.get('type') != 'file':
                        data[value['title']] = format_value(value.get('type', 'object'))
            return data if len(data) > 0 else None

    def get_swagger_request_files(self, value: Union[str, dict]) -> Union[dict, None]:
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
            return files if len(files) > 0 else None
        else:
            if not isinstance(value, dict):
                schema_data = self.get_swagger_schema_data(value)
                for k, v in schema_data['properties'].items():
                    if v.get('format') == 'binary':
                        files[k] = format_value(v.get('type', 'object'))
                return files if len(files) > 0 else None
