#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os.path
from pathlib import Path
from typing import NoReturn

import typer

from httpfpt.core.get_conf import PROJECT_NAME
from httpfpt.core.path_conf import TEST_CASE_PATH
from httpfpt.utils.file_control import search_all_case_yaml_files, search_all_testcase_files, get_file_property


def auto_generate_testcases(rewrite: bool = False) -> NoReturn:
    """
    自动创建测试用例

    :param rewrite:
    :return:
    """
    # 获取所用用例数据文件
    yaml_datafiles = search_all_case_yaml_files()
    if len(yaml_datafiles) == 0:
        raise ValueError('自动生成用例失败，未在指定项目下找到测试用例数据文件，请检查项目目录是否正确')

    # 获取所有测试用例文件
    testcase_files = search_all_testcase_files()

    # 获取所有用例文件名
    yaml_filenames = []
    yaml_file_root_names = []
    for _ in yaml_datafiles:
        yaml_filenames.append(get_file_property(_)[0])
        yaml_file_root_names.append(get_file_property(_)[1])

    # 获取所有测试用例文件名
    testcase_filenames = []
    for _ in testcase_files:
        testcase_filenames.append(get_file_property(_)[0])

    # 获取需要创建的测试用例文件名
    create_file_root_names = []
    for root_name in yaml_file_root_names:
        if not rewrite:
            if (
                (root_name if root_name.startswith('test_') else 'test_' + root_name) + '.py'
            ) not in testcase_filenames:
                create_file_root_names.append(root_name)
        else:
            create_file_root_names.append(root_name)
    if len(create_file_root_names) == 0:
        typer.secho('😝 用例已经很完善了, 添加新测试用例数据后再来生成吧~', fg='green', bold=True)
        return

    typer.secho('⏳ 疯狂自动生成中...', fg='green', bold=True)

    for create_file_root_name in create_file_root_names:
        for yaml_filename in yaml_filenames:
            if create_file_root_name == get_file_property(yaml_filename)[1]:
                testcase_class_name = ''.join(name.title() for name in create_file_root_name.split('_'))
                testcase_func_name = create_file_root_name
                if not create_file_root_name.startswith('test_'):
                    testcase_class_name = 'Test' + testcase_class_name
                    testcase_func_name = 'test_' + testcase_func_name
                case_code = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

import allure
import pytest

from httpfpt.common.send_request import send_request
from httpfpt.common.yaml_handler import read_yaml
from httpfpt.core.get_conf import PROJECT_NAME
from httpfpt.utils.request.case_data_file_parse import get_request_data
from httpfpt.utils.request.ids_extract import get_ids

request_data = get_request_data(
    file_data=read_yaml(filename=os.sep.join([PROJECT_NAME, '{yaml_filename}'])), use_pydantic_verify=False
)
allure_text = request_data[0]['config']['allure']
request_ids = get_ids(request_data)


@allure.epic(allure_text['epic'])
@allure.feature(allure_text['feature'])
class {testcase_class_name}:
    """{testcase_class_name.replace('Test', '')}"""

    @allure.story(allure_text['story'])
    @pytest.mark.parametrize('data', request_data, ids=request_ids)
    def {testcase_func_name}(self, data):
        """{create_file_root_name}"""
        send_request.send_request(data)
'''
                # 创建测试用例文件
                tag = str(Path(yaml_filename).parent)[1:]
                if tag != '':
                    case_path = os.path.join(TEST_CASE_PATH, PROJECT_NAME, tag, testcase_func_name + '.py')
                else:
                    case_path = os.path.join(TEST_CASE_PATH, PROJECT_NAME, testcase_func_name + '.py')
                if not Path(case_path).parent.exists():
                    Path(case_path).parent.mkdir(parents=True, exist_ok=True)
                with open(case_path, 'w', encoding='utf-8') as f:
                    f.write(case_code)
                typer.secho(f'📄 Created: {get_file_property(case_path)[0]}', fg='green', bold=True)

    typer.secho('✅ 测试用例自动生成完成', fg='green', bold=True)
