#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import sys

from typing import Tuple

import cappa

from cappa import Subcommands
from pydantic import ValidationError
from rich.prompt import Confirm
from typing_extensions import Annotated  # noqa: TCH002

sys.path.append('..')

from httpfpt.common.yaml_handler import read_yaml
from httpfpt.schemas.case_data import CaseData
from httpfpt.utils.case_auto_generator import auto_generate_testcases
from httpfpt.utils.data_manage.apifox import ApiFoxParser
from httpfpt.utils.data_manage.git_repo import GitRepoPaser
from httpfpt.utils.data_manage.openapi import SwaggerParser
from httpfpt.utils.file_control import search_all_case_yaml_files
from httpfpt.utils.rich_console import console


def get_version() -> None:
    """获取版本号"""
    ver = open('./__init__.py', 'rt').read()
    mob = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", ver, re.M)
    if mob:
        console.print('\n🔥 HttpFpt', mob.group(1))
    else:
        raise RuntimeError('未查询到版本号')


def testcase_data_verify(verify: str) -> None:
    """测试数据验证"""
    msg: str = ''
    try:
        count: int = 0
        if verify.lower() == 'all':
            console.print('\n🔥 开始验证所有测试数据结构...')
            file_list = search_all_case_yaml_files()
            for file in file_list:
                file_data = read_yaml(None, filename=file)
                CaseData.model_validate(file_data)
        else:
            console.print(f'🔥 开始验证 {verify} 测试数据结构...')
            file_data = read_yaml(None, filename=verify)
            CaseData.model_validate(file_data)
    except ValidationError as e:
        count = e.error_count()
        msg += str(e)
    except Exception as e:
        console.print(f'❌ 验证测试数据 {verify} 结构失败: {e}')
        raise cappa.Exit(code=1)
    if count > 0:
        console.print(f'❌ 验证测试数据 {verify} 结构失败: {msg}')
        raise cappa.Exit(code=1)
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
        console.print(f'❌ 自动生成测试用例失败: {e}')
        raise cappa.Exit(code=1)


def import_openapi_case_data(openapi: Tuple[str, str]) -> None:
    """导入 openapi 测试用例数据"""
    console.print(f'\n📩 正在导入测试用例数据到项目: [#0087ff]{openapi[1]}[/#0087ff]')
    result = Confirm.ask('❓ 确认执行此操作吗?', default=False)
    if result:
        console.print('🔥 开始导入 openapi 数据...')
        try:
            SwaggerParser().import_openapi_to_yaml(openapi[0], openapi[1])
        except Exception as e:
            console.print('❌ 导入 openapi 数据失败')
            raise e


def import_apifox_case_data(apifox: Tuple[str, str]) -> None:
    """导入 apifox 测试用例数据"""
    console.print(
        '\n'
        'Beta: 此命令目前处于测试阶段, 请谨慎使用。\n'
        'Warning: 如果现有文件名与导入文件名相同, 此命令目前会覆盖写入用例数据, 请谨慎操作。\n',
        style='bold #ffd700',
    )
    result = Confirm.ask('⚠️ 确认执行此操作吗?', default=False)
    if result:
        console.print('🔥 开始导入 apifox 数据...')
        try:
            ApiFoxParser().import_apifox_to_yaml(apifox[0], apifox[1])
        except Exception as e:
            console.print('❌ 导入 apifox 数据失败:')
            raise e


def import_har_case_data(har: Tuple[str, str]) -> None:
    """导入 har 测试用例数据"""
    console.print('\n🚧 此功能暂未开发')


def import_jmeter_case_data(jmeter: Tuple[str, str]) -> None:
    """导入 jmeter 测试用例数据"""
    console.print('\n🚧 此功能暂未开发')


def import_postman_case_data(postman: Tuple[str, str]) -> None:
    """导入 postman 测试用例数据"""
    console.print('\n🚧 此功能暂未开发')


def import_git_case_data(src: str) -> None:
    """导入 git 仓库测试数据"""
    console.print(f'\n🚀 正在导入 git 仓库测试数据到本地: {src}')
    console.print('🔥 开始导入 git 仓库测试数据...\n')
    try:
        GitRepoPaser.import_git_to_local(src)
    except Exception as e:
        console.print(f'❌ 导入 git 仓库测试数据失败: {e}')
        raise e


def httpfpt_cli(httpfpt: HttpFptCLI) -> None:
    """CLI 入口"""
    if httpfpt.version:
        get_version()
    if httpfpt.subcmd:
        if isinstance(httpfpt.subcmd, TestCaseCLI):
            data_verify = httpfpt.subcmd.data_verify
            generate = httpfpt.subcmd.generate
            if data_verify:
                testcase_data_verify(data_verify)
            if generate:
                generate_testcases()
        if isinstance(httpfpt.subcmd, ImportCLI):
            openai = httpfpt.subcmd.openai
            apifox = httpfpt.subcmd.apifox
            har = httpfpt.subcmd.har
            jmeter = httpfpt.subcmd.jmeter
            postman = httpfpt.subcmd.postman
            git = httpfpt.subcmd.git
            if openai:
                import_openapi_case_data(openai)
            if apifox:
                import_apifox_case_data(apifox)
            if har:
                import_har_case_data(har)
            if jmeter:
                import_jmeter_case_data(jmeter)
            if postman:
                import_postman_case_data(postman)
            if git:
                import_git_case_data(git)


@cappa.command(name='httpfpt-cli', invoke=httpfpt_cli)
class HttpFptCLI:
    version: Annotated[
        bool,
        cappa.Arg(
            short='-V',
            long=True,
            default=False,
            help='Print version information.',
        ),
    ]
    subcmd: Subcommands[TestCaseCLI | ImportCLI | None] = None


@cappa.command(name='testcase', help='Test case tools', invoke=httpfpt_cli)
class TestCaseCLI:
    data_verify: Annotated[
        str,
        cappa.Arg(
            value_name='<FILENAME / ALL>',
            short='-dv',
            long=True,
            default='',
            help='验证测试数据结构；当指定文件时, 仅验证指定文件, 当指定 "all" 时, 验证所有文件.',
            required=False,
        ),
    ]
    generate: Annotated[
        bool,
        cappa.Arg(
            short='-gt',
            long=True,
            default=False,
            help='自动生成测试用例.',
            required=False,
        ),
    ]


@cappa.command(name='import', help='Import test case data', invoke=httpfpt_cli)
class ImportCLI:
    openai: Annotated[
        Tuple[str, str],
        cappa.Arg(
            value_name='<JSONFILE / URL> <PROJECT>',
            short='-io',
            long='--import-openapi',
            default=(),
            help='导入 openapi 数据到 yaml 数据文件; 支持 json 文件 / url 导入, 需要指定 project 项目名.',
            required=False,
        ),
    ]
    apifox: Annotated[
        Tuple[str, str],
        cappa.Arg(
            value_name='<JSONFILE> <PROJECT>',
            short='-ia',
            long='--import-apifox',
            default=(),
            help='Beta: 导入 apifox 数据到 yaml 数据文件; 支持 json 文件导入, 需要指定 project 项目名.',
            required=False,
        ),
    ]
    har: Annotated[
        Tuple[str, str],
        cappa.Arg(
            short='-ih',
            long='--import-har',
            default=(),
            help='TODO: Not started yet.',
            required=False,
        ),
    ]
    jmeter: Annotated[
        Tuple[str, str],
        cappa.Arg(
            short='-ij',
            long='--import-jmeter',
            default=(),
            help='TODO: Not started yet.',
            required=False,
        ),
    ]
    postman: Annotated[
        Tuple[str, str],
        cappa.Arg(
            short='-ip',
            long='--import-postman',
            default=(),
            help='TODO: Not started yet.',
            required=False,
        ),
    ]
    git: Annotated[
        str,
        cappa.Arg(
            value_name='<GIT HTTPS>',
            short='-ig',
            long='--import-git',
            default='',
            help='导入 git 仓库测试数据到本地.',
            required=False,
        ),
    ]


if __name__ == '__main__':
    cappa.invoke(HttpFptCLI)
