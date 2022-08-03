#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glob
import os.path

from fastpt.common.log import log
from fastpt.core.get_conf import PROJECT_NAME
from fastpt.core.path_conf import YAML_DATA_PATH, TEST_CASE_PATH
from fastpt.utils.file_control import search_all_case_yaml_files, search_all_test_case_files, get_file_property


def auto_generate_test_cases():
    """
    自动创建测试用例

    :return:
    """
    yaml_files = search_all_case_yaml_files()
    test_case_files = search_all_test_case_files()
    if len(yaml_files) == 0:
        raise ValueError('自动生成用例失败，未在指定项目下找到测试用例数据文件，请检查项目目录是否正确')

    yaml_file_names = []
    yaml_file_root_names = []
    for _ in yaml_files:
        _property = get_file_property(_)
        yaml_file_names.append(_property[0])
        yaml_file_root_names.append(_property[1])

    test_case_file_names = []
    for _ in test_case_files:
        test_case_file_names.append(get_file_property(_)[0])

    create_list_file_root_name = []
    for _ in yaml_file_root_names:
        if (_ + '.py') not in test_case_file_names:
            create_list_file_root_name.append(_)
    if len(create_list_file_root_name) == 0:
        log.info('用例已经很完善了, 添加新用例后再来生成吧~')
        return

    yaml_data_files = []
    for _ in create_list_file_root_name:
        data_file = glob.glob(os.path.join(YAML_DATA_PATH, f'{PROJECT_NAME}', '**\\', f'{_}.*ml'), recursive=True)[0]
        yaml_data_files.append(data_file)

    for data in yaml_data_files:
        filename = get_file_property(data)[0]
        file_root_name = get_file_property(data)[1]
        filepath = data.replace(YAML_DATA_PATH, '')
        read_filename = "\\".join(filepath.split('\\')[1:])  # todo
        class_title = ''.join(name.title() for name in file_root_name.split('_'))
        func_title = file_root_name
        if not filename.startswith('test'):
            class_title = 'Test' + class_title
            func_title = 'test_' + func_title
        case_code = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import allure
import pytest

from fastpt.common.send_request import send_request
from fastpt.common.yaml_handler import read_yaml
from fastpt.utils.request.file_data_parse import get_request_data
from fastpt.utils.request.ids_extract import get_ids

request_data = get_request_data(read_yaml(filename=r'{read_filename}'))

allure_text = request_data[0]['config']['allure']


@allure.epic(allure_text['epic'])
@allure.feature(allure_text['feature'])
class {class_title}:

    request_ids = get_ids(request_data)

    @allure.story(allure_text['story'])
    # @pytest.mark.???
    @pytest.mark.parametrize('data', request_data, ids=request_ids)
    def {func_title}(self, data):
        """ {{0}} """ .format(data['test_steps']['description'])
        send_request.send_request(data)
        '''
        case_path = os.path.join(TEST_CASE_PATH + (filepath.split('.')[0] + '.py'))  # todo
        if not os.path.exists(case_path):
            with open(case_path, 'w', encoding='utf-8') as f:
                f.write(case_code)

    log.success('测试用例自动生成完成')


if __name__ == '__main__':
    auto_generate_test_cases()
