#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy
import os

from httpfpt.common.json_handler import read_json_file
from httpfpt.common.yaml_handler import write_yaml
from httpfpt.core.get_conf import httpfpt_config
from httpfpt.core.path_conf import httpfpt_path
from httpfpt.utils.data_manage.base_format import format_value
from httpfpt.utils.file_control import get_file_property
from httpfpt.utils.rich_console import console


class ApiFoxParser:
    def import_apifox_to_yaml(self, source: str, project: str | None = None) -> None:
        """
        导入 apifox 数据到 yaml

        :param source:
        :param project:
        :return:
        """
        data = read_json_file(source)
        apifox = data.get('apifoxProject')
        if not apifox:
            raise ValueError('获取 apifox 数据失败，请使用合法的 apifox 文件')
        if apifox != '1.0.0':
            raise Exception('不受支持的 apifox 版本')
        try:
            case_config = {}
            case_config.update(
                {
                    'allure': {
                        'epic': data['info']['name'],
                        'feature': data['tags'][0]['name'] if data.get('tags') is not None else '未知',
                        'story': data['info']['description'],
                    },
                    'request': {'env': 'dev.env'},
                    'module': data['info']['name'],
                }
            )
            tag_case = {}
            root_case = {}
            for i in data['apiCollection'][0]['items']:
                if i.get('items') is None:
                    case = self.get_apifox_step(i)
                    root_case = copy.deepcopy(root_case)
                    if root_case.get('root') is None:
                        root_case.update({'root': [case]})
                    else:
                        root_case['root'].append(case)
                # 多级子目录数据
                else:
                    pass  # todo 二叉树数据解析
            if (len(tag_case) or len(root_case)) > 0:
                console.print('⏳ 奋力导入中...')
            # 写入项目 tag 目录
            if len(tag_case) > 0:
                for k, v in tag_case.items():
                    case_config['allure']['feature'] = case_config['module'] = k
                    case_file_data = {'config': case_config, 'test_steps': v}
                    write_yaml(
                        httpfpt_path.case_data_dir,
                        os.sep.join(
                            [project or httpfpt_config.PROJECT_NAME, k, get_file_property(source)[1] + '.yaml']
                        ),
                        case_file_data,
                        mode='w',
                    )
            # 写入项目根目录
            if len(root_case) > 0:
                for v in root_case.values():
                    case_file_data = {'config': case_config, 'test_steps': v}
                    write_yaml(
                        httpfpt_path.case_data_dir,
                        os.sep.join([project or httpfpt_config.PROJECT_NAME, get_file_property(source)[1] + '.yaml']),
                        case_file_data,
                        mode='w',
                    )
            console.print('✅ 导入 apifox 数据成功')
        except Exception as e:
            raise e

    @staticmethod
    def get_apifox_params(value: dict) -> dict | None:
        """
        获取查询参数

        :param value:
        :return:
        """
        data = {}
        params = value.get('query')
        if params is not None:
            for i in params:
                if i['type'] != 'file':
                    data[i['name']] = format_value(i.get('type', 'object'))
        return data if len(data) > 0 else None

    @staticmethod
    def get_apifox_headers(value: dict) -> dict | None:
        """
        获取查询参数

        :param value:
        :return:
        """
        data = {}
        header_type = value['type']
        if header_type != 'none':
            data = {'Content-Type': f'{header_type}'}
        return data if len(data) > 0 else None

    @staticmethod
    def get_apifox_request_data(value: dict) -> dict | None:
        """
        获取请求 data

        :param value:
        :return:
        """
        body = {}
        data = value.get('jsonSchema')
        if data is not None:
            for k, v in data['properties'].items():
                body[k] = format_value(v.get('type', 'object'))
        return body if len(body) > 0 else None

    @staticmethod
    def get_apifox_request_files(value: dict) -> dict | None:
        """
        获取请求 files

        :param value:
        :return:
        """
        files = {}
        data = value.get('parameters')
        if data is not None and len(data) > 0:
            for i in data:
                if i.get('type') == 'file':
                    files[i['name']] = format_value('object')
        return files if len(files) > 0 else None

    def get_apifox_step(self, value: dict) -> dict:
        """
        获取 apifox 用例

        :param value:
        :return:
        """
        params = self.get_apifox_params(value['api']['parameters'])
        headers = self.get_apifox_headers(value['api']['requestBody'])
        data_type = None
        if headers is not None:
            data_type = 'json' if 'application/json' in headers else 'data'
        data = self.get_apifox_request_data(value['api']['requestBody'])
        files = self.get_apifox_request_files(value['api']['requestBody'])
        case_id = value.get('api').get('operationId')
        case = {
            'name': value.get('name'),
            'case_id': case_id if case_id is not None or case_id != '' else value.get('api').get('id'),
            'description': value.get('api').get('description'),
            'is_run': True if value.get('status') in ['released', 'tested'] else False,
            'request': {
                'method': value.get('api').get('method'),
                'url': value.get('api').get('path'),
                'params': params,
                'headers': headers,
                'data_type': data_type,
                'data': data,
                'files': files,
            },
        }
        return case
