#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os.path

from pathlib import Path

from httpfpt.core.get_conf import httpfpt_config
from httpfpt.core.path_conf import httpfpt_path
from httpfpt.utils.file_control import get_file_property, search_all_case_data_files, search_all_testcase_files
from httpfpt.utils.rich_console import console


def auto_generate_testcases(rewrite: bool = False) -> None:
    """
    自动创建测试用例

    :param rewrite:
    :return:
    """
    # 获取所用用例数据文件
    case_data_files = search_all_case_data_files()
    if len(case_data_files) == 0:
        raise FileNotFoundError('自动生成用例失败，未在指定项目下找到测试用例数据文件，请检查项目目录是否正确')

    # 获取所有测试用例文件
    testcase_files = search_all_testcase_files()

    # 获取所有用例文件名
    case_filenames = []
    case_file_root_names = []
    for _ in case_data_files:
        case_filenames.append(_)
        case_file_root_names.append(get_file_property(_)[1])

    # 获取所有测试用例数据文件名
    testcase_filenames = []
    for _ in testcase_files:
        testcase_filenames.append(get_file_property(_)[0])

    # 获取需要创建的测试用例文件名
    create_file_root_names = []
    for root_name in case_file_root_names:
        if not rewrite:
            if (
                (root_name if root_name.startswith('test_') else 'test_' + root_name) + '.py'
            ) not in testcase_filenames:
                create_file_root_names.append(root_name)
        else:
            create_file_root_names.append(root_name)
    if len(create_file_root_names) == 0:
        console.print('😝 用例已经很完善了, 添加新测试用例数据后再来生成吧~')
        return

    console.print('⏳ 疯狂自动生成中...')

    for create_file_root_name in create_file_root_names:
        for case_filename in case_filenames:
            file_property = get_file_property(case_filename)
            if create_file_root_name == file_property[1]:
                testcase_class_name = ''.join(name.title() for name in create_file_root_name.split('_'))
                testcase_func_name = create_file_root_name
                if not create_file_root_name.startswith('test_'):
                    testcase_class_name = 'Test' + testcase_class_name
                    testcase_func_name = 'test_' + testcase_func_name
                case_code = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import allure
import pytest

from httpfpt.common.send_request import send_request
from httpfpt.utils.request.case_data_parse import get_testcase_data

allure_data, ddt_data, ids = get_testcase_data(filename='{file_property[0]}')


@allure.epic(allure_data['epic'])
@allure.feature(allure_data['feature'])
class {testcase_class_name}:
    """{testcase_class_name.replace('Test', '')}"""

    @allure.story(allure_data['story'])
    @pytest.mark.parametrize('data', ddt_data, ids=ids)
    def {testcase_func_name}(self, data):
        """{create_file_root_name}"""
        send_request.send_request(data)
'''
                # 创建测试用例文件
                tag = case_filename.split(httpfpt_config.PROJECT_NAME)[1].split(os.path.sep)[1:-1]
                new_testcase_filename = testcase_func_name + '.py'
                if tag:
                    case_path = os.path.join(
                        httpfpt_path.testcase_dir, httpfpt_config.PROJECT_NAME, *tag, new_testcase_filename
                    )
                else:
                    case_path = os.path.join(
                        httpfpt_path.testcase_dir, httpfpt_config.PROJECT_NAME, new_testcase_filename
                    )
                new_testcase_dir = Path(case_path).parent  # type: ignore
                if not new_testcase_dir.exists():
                    new_testcase_dir.mkdir(parents=True, exist_ok=True)
                Path(str(case_path)).write_text(case_code, encoding='utf-8')
                console.print(f'📄 Created: {new_testcase_filename}')

    console.print('✅ 测试用例自动生成完成')
