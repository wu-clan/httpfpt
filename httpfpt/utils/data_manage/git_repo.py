#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import shutil

from pydantic import ValidationError

from httpfpt.common.json_handler import read_json_file
from httpfpt.common.yaml_handler import read_yaml
from httpfpt.enums.case_data_type import CaseDataType
from httpfpt.schemas.case_data import CaseData
from httpfpt.utils.file_control import get_file_property, search_all_case_data_files
from httpfpt.utils.pydantic_parser import parse_error
from httpfpt.utils.rich_console import console


class GitRepoPaser:
    @staticmethod
    def import_git_to_local(src: str) -> None:
        """
        导入 git 仓库测试数据

        :param src:
        :return:
        """

        if 'https' not in src:
            raise ValueError('❌ Git 仓库克隆地址错误, 请使用 https 地址')

        try:
            online_dir_path = os.path.join(os.path.abspath('./data/test_data'), 'online_test_data')
            console.print(online_dir_path)
            if os.path.exists(online_dir_path):
                shutil.rmtree(online_dir_path)
            os.makedirs(online_dir_path)
            result = os.system(f'cd {online_dir_path} && git clone {src}')
            shutil.rmtree(os.path.join(online_dir_path, '.git'))
        except Exception as e:
            raise RuntimeError(f'❌ Git 仓库测试数据拉取失败：{e}')
        if result == 0:
            console.print('\n✅ Git 仓库数据文件拉取成功')
        else:
            raise RuntimeError('❌ Git 仓库测试数据拉取失败，请检查 Git 地址是否正确')

        console.print('\n🔥 开始自动验证测试数据结构...')
        all_case_data_file = search_all_case_data_files(online_dir_path)
        if len(all_case_data_file) == 0:
            raise FileNotFoundError('❌ 未在拉取的 Git 仓库中找到测试用例数据文件，请检查 Git 地址是否正确')
        all_case_data = []
        for file in all_case_data_file:
            file_type = get_file_property(file)[2]
            if file_type == CaseDataType.JSON:
                file_data = read_json_file(file)
            else:
                file_data = read_yaml(file)
            all_case_data.append(file_data)
        count: int = 0
        for case_data in all_case_data:
            try:
                CaseData.model_validate(case_data)
            except ValidationError as e:
                count += parse_error(e)
        if count > 0:
            raise ValueError(f'❌ Git 仓库用例数据校验失败，共有 {count} 处错误, 错误详情请查看日志')
