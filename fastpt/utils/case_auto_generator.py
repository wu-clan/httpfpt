#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os.path
from pathlib import Path

import typer

from fastpt.core.get_conf import PROJECT_NAME
from fastpt.core.path_conf import TEST_CASE_PATH
from fastpt.utils.file_control import search_all_case_yaml_files, search_all_test_case_files, get_file_property


def auto_generate_test_cases(rewrite: bool = False) -> None:
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
    testcase_files = search_all_test_case_files()

    # 获取所有用例文件名
    yaml_filenames = []
    yaml_file_root_names = []
    for _ in yaml_datafiles:
        pp = get_file_property(_)
        yaml_filenames.append(pp[0])
        yaml_file_root_names.append(pp[1])

    # 获取所有测试用例文件名
    testcase_filenames = []
    for _ in testcase_files:
        testcase_filenames.append(get_file_property(_)[0])

    # 获取需要创建的测试用例文件名
    create_file_root_names = []
    for name in yaml_file_root_names:
        if not rewrite:
            if ((name if name.startswith('test_') else 'test_' + name) + '.py') not in testcase_filenames:
                create_file_root_names.append(name)
        else:
            create_file_root_names.append(name)
    if len(create_file_root_names) == 0:
        typer.secho('😝 用例已经很完善了, 添加新测试用例数据后再来生成吧~', fg='green', bold=True)
        return

    typer.secho('⏳ 疯狂自动生成中...', fg='green', bold=True)

    for create_file_root_name in create_file_root_names:
        for yaml_filename in yaml_filenames:
            if create_file_root_name == Path(yaml_filename).stem:
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

from fastpt.common.send_request import send_request
from fastpt.common.yaml_handler import read_yaml
from fastpt.core.get_conf import PROJECT_NAME
from fastpt.utils.request.file_data_parse import get_request_data
from fastpt.utils.request.ids_extract import get_ids

request_data = get_request_data(read_yaml(filename=os.sep.join([PROJECT_NAME, '{yaml_filename}'])))
allure_text = request_data[0]['config']['allure']
request_ids = get_ids(request_data)


@allure.epic(allure_text['epic'])
@allure.feature(allure_text['feature'])
class {testcase_class_name}:

    @allure.story(allure_text['story'])
    # @pytest.mark.???
    @pytest.mark.parametrize('data', request_data, ids=request_ids)
    def {testcase_func_name}(self, data):
        """ {{0}} """.format(data['test_steps']['description'] or '未知')
        send_request.send_request(data)
        '''
                # 创建测试用例文件
                case_path = os.path.join(TEST_CASE_PATH, PROJECT_NAME, testcase_func_name + '.py')
                with open(case_path, 'w', encoding='utf-8') as f:
                    f.write(case_code)

    typer.secho('✅ 测试用例自动生成完成', fg='green', bold=True)
