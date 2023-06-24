#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import shutil

import typer
from pydantic import ValidationError

from httpfpt.common.yaml_handler import read_yaml
from httpfpt.schemas.case_data import CaseData
from httpfpt.utils.file_control import search_all_case_yaml_files
from httpfpt.utils.pydantic_error_parse import parse_error


class GitRepoPaser:
    @staticmethod
    def import_git_to_local(src: str) -> None:
        """
        导入 git 仓库测试数据

        :param src:
        :return:
        """

        if 'https' not in src:
            raise ValueError('❌ git 仓库克隆地址错误, 请使用 https 地址')

        try:
            online_dir_path = os.path.join(os.path.abspath('./data/test_data'), 'online_test_data')
            typer.echo(online_dir_path)
            if os.path.exists(online_dir_path):
                shutil.rmtree(online_dir_path)
            os.makedirs(online_dir_path)
            result = os.system(f'cd {online_dir_path} && git clone {src}')
        except Exception as e:
            raise RuntimeError(f'❌ git 仓库测试数据拉取失败：{e}')
        else:
            if result == 0:
                typer.secho('✅ git 仓库数据文件拉取成功')
            else:
                raise RuntimeError('❌ git 仓库测试数据拉取失败')

        all_yaml_file = search_all_case_yaml_files(online_dir_path)
        all_case_data = []
        for file in all_yaml_file:
            read_data = read_yaml(None, filename=file)
            all_case_data.append(read_data)
        for case_data in all_case_data:
            try:
                count: int = 0
                CaseData.model_validate(case_data, strict=True)
            except ValidationError as e:
                count = parse_error(e)
            if count > 0:
                raise ValueError(f'用例数据校验失败，共有 {count} 处错误, 错误详情请查看日志')
