#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os.path

import cappa

from pydantic import ValidationError
from rich.prompt import Confirm

from httpfpt.common.json_handler import read_json_file
from httpfpt.common.yaml_handler import read_yaml
from httpfpt.core.get_conf import httpfpt_config
from httpfpt.core.path_conf import httpfpt_path
from httpfpt.enums.case_data_type import CaseDataType
from httpfpt.schemas.case_data import CaseData
from httpfpt.utils.case_auto_generator import auto_generate_testcases
from httpfpt.utils.file_control import get_file_property, search_all_case_data_files
from httpfpt.utils.rich_console import console


def testcase_data_verify(verify: str) -> None:
    """测试数据验证"""
    msg: str = ''
    try:
        count: int = 0
        if verify.lower() == 'all':
            console.print('\n🔥 开始验证所有测试数据结构...')
            file_list = search_all_case_data_files()
            for file in file_list:
                file_type = get_file_property(file)[2]
                if file_type == CaseDataType.JSON:
                    file_data = read_json_file(file)
                else:
                    file_data = read_yaml(file)
                CaseData.model_validate(file_data)
        else:
            console.print(f'🔥 开始验证 {verify} 测试数据结构...')
            file_type = get_file_property(verify)[2]
            if os.path.isfile(verify):
                data_path = os.path.join(httpfpt_path.case_data_dir, httpfpt_config.PROJECT_NAME)
                if file_type == CaseDataType.JSON:
                    file_data = read_json_file(str(data_path), verify)
                else:
                    file_data = read_yaml(str(data_path), verify)
            else:
                if file_type == CaseDataType.JSON:
                    file_data = read_json_file(verify)
                else:
                    file_data = read_yaml(verify)
            CaseData.model_validate(file_data)
    except ValidationError as e:
        count = e.error_count()
        msg += str(e)
    except Exception as e:
        console.print(f'\n❌ 验证测试数据 {verify} 结构失败: {e}')
        raise e
    if count > 0:
        raise cappa.Exit(f'\n❌ 验证测试数据 {verify} 结构失败: {msg}', code=1)
    else:
        console.print('✅ 验证测试数据结构成功')


def generate_testcases() -> None:
    """生成测试用例"""
    console.print(
        '\n'
        'Warning: 此操作生成的测试用例是依赖测试数据文件而决定的,\n'
        '         如果你手动创建的测试用例与测试数据文件名称相吻合,\n'
        '         那么此操作将不能完全保证你的手动创建测试用例继续保留,\n'
        '         如果你依然执行此操作, 请谨慎选择重新生成所有测试用例。\n',
        style='bold #ffd700',
    )
    result = Confirm.ask('⚠️ 是否重新生成所有测试用例?', default=False)
    try:
        if result:
            console.print('🔥 开始重新生成所有测试用例...')
            auto_generate_testcases(rewrite=True)
        else:
            console.print('🔥 开始生成新测试用例...')
            auto_generate_testcases()
    except Exception as e:
        console.print(f'\n❌ 自动生成测试用例失败: {e}')
        raise e
