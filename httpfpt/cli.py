from __future__ import annotations

import os
import sys

from dataclasses import dataclass

import cappa

from cappa import Subcommands
from pydantic import ValidationError
from rich.prompt import Confirm
from rich.traceback import install as rich_install
from typing_extensions import Annotated

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from httpfpt import __version__
from httpfpt.common.json_handler import read_json_file
from httpfpt.common.yaml_handler import read_yaml
from httpfpt.core.get_conf import httpfpt_config
from httpfpt.core.path_conf import httpfpt_path
from httpfpt.enums.case_data_type import CaseDataType
from httpfpt.run import run
from httpfpt.schemas.case_data import CaseData
from httpfpt.utils.case_auto_generator import auto_generate_testcases
from httpfpt.utils.data_manage.apifox import ApiFoxParser
from httpfpt.utils.data_manage.git_repo import GitRepoPaser
from httpfpt.utils.data_manage.openapi import SwaggerParser
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


def import_openapi_case_data(openapi: tuple[str, str]) -> None:
    """导入 openapi 测试用例数据"""
    console.print(f'\n📩 正在导入测试用例数据到项目: [#0087ff]{openapi[1]}[/#0087ff]')
    result = Confirm.ask('❓ 确认执行此操作吗?', default=False)
    if result:
        console.print('🔥 开始导入 openapi 数据...')
        try:
            SwaggerParser().import_openapi_to_yaml(openapi[0], openapi[1])
        except Exception as e:
            console.print('\n❌ 导入 openapi 数据失败')
            raise e


def import_apifox_case_data(apifox: tuple[str, str]) -> None:
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
            console.print('\n❌ 导入 apifox 数据失败:')
            raise e


def import_har_case_data(har: tuple[str, str]) -> None:
    """导入 har 测试用例数据"""
    console.print('\n🚧 此功能暂未开发')


def import_jmeter_case_data(jmeter: tuple[str, str]) -> None:
    """导入 jmeter 测试用例数据"""
    console.print('\n🚧 此功能暂未开发')


def import_postman_case_data(postman: tuple[str, str]) -> None:
    """导入 postman 测试用例数据"""
    console.print('\n🚧 此功能暂未开发')


def import_git_case_data(src: str) -> None:
    """导入 git 仓库测试数据"""
    console.print(f'\n🚀 正在导入 git 仓库测试数据到本地: {src}')
    console.print('🔥 开始导入 git 仓库测试数据...\n')
    try:
        GitRepoPaser.import_git_to_local(src)
    except Exception as e:
        console.print(f'\n❌ 导入 git 仓库测试数据失败: {e}')
        raise e


@cappa.command(name='httpfpt-cli')
@dataclass
class HttpFptCLI:
    run_test: Annotated[
        list[str] | None,
        cappa.Arg(
            value_name='<PYTEST ARGS>',
            short='-r',
            long='--run',
            default=None,
            show_default=False,
            help='Run test cases, do not support use with other commands, but support custom pytest running parameters,'
            ' default parameters see `httpfpt/run.py`.',
            num_args=-1,
        ),
    ]
    subcmd: Subcommands[TestCaseCLI | ImportCLI | None] = None

    def __call__(self) -> None:
        if self.run_test is not None:
            if self.subcmd:
                console.print('\n❌ 不支持 -r/--run 命令与其他 CLI 命令同时使用')
                raise cappa.Exit(code=1)
            run(*self.run_test)
        else:
            run()


@cappa.command(name='testcase', help='Test case tools.')
@dataclass
class TestCaseCLI:
    data_verify: Annotated[
        str,
        cappa.Arg(
            value_name='<FILENAME / ALL>',
            short='-c',
            long=True,
            default='',
            help='验证测试数据结构；当指定文件（文件名/绝对路径）时, 仅验证指定文件, 当指定 "all" 时, 验证所有文件.',
            required=False,
        ),
    ]
    generate: Annotated[
        bool,
        cappa.Arg(
            short='-g',
            long=True,
            default=False,
            help='自动生成测试用例.',
            required=False,
        ),
    ]

    def __call__(self) -> None:
        if self.data_verify:
            testcase_data_verify(self.data_verify)
        if self.generate:
            generate_testcases()


@cappa.command(name='import', help='Import testcase data.')
@dataclass
class ImportCLI:
    openai: Annotated[
        tuple[str, str],
        cappa.Arg(
            value_name='<JSONFILE / URL> <PROJECT>',
            short='-openapi',
            long='--import-openapi',
            default=(),
            help='导入 openapi 数据到 yaml 数据文件; 支持 json 文件 / url 导入, 需要指定 project 项目名.',
            required=False,
        ),
    ]
    apifox: Annotated[
        tuple[str, str],
        cappa.Arg(
            value_name='<JSONFILE> <PROJECT>',
            short='-apifox',
            long='--import-apifox',
            default=(),
            help='Beta: 导入 apifox 数据到 yaml 数据文件; 支持 json 文件导入, 需要指定 project 项目名.',
            required=False,
        ),
    ]
    har: Annotated[
        tuple[str, str],
        cappa.Arg(
            value_name='<HAR> <PROJECT>',
            short='-har',
            long='--import-har',
            default=(),
            help='TODO: Not started yet.',
            required=False,
        ),
    ]
    jmeter: Annotated[
        tuple[str, str],
        cappa.Arg(
            value_name='<JMETER> <PROJECT>',
            short='-jmeter',
            long='--import-jmeter',
            default=(),
            help='TODO: Not started yet.',
            required=False,
        ),
    ]
    postman: Annotated[
        tuple[str, str],
        cappa.Arg(
            value_name='<POSTMAN> <PROJECT>',
            short='-postman',
            long='--import-postman',
            default=(),
            help='TODO: Not started yet.',
            required=False,
        ),
    ]
    git: Annotated[
        str,
        cappa.Arg(
            value_name='<GIT URL>',
            short='-git',
            long='--import-git',
            default='',
            help='导入 git 仓库测试数据到本地.',
            required=False,
        ),
    ]

    def __call__(self) -> None:
        if self.openai:
            import_openapi_case_data(self.openai)
        if self.apifox:
            import_apifox_case_data(self.apifox)
        if self.har:
            import_har_case_data(self.har)
        if self.jmeter:
            import_jmeter_case_data(self.jmeter)
        if self.postman:
            import_postman_case_data(self.postman)
        if self.git:
            import_git_case_data(self.git)


def main() -> None:
    """cli 执行程序"""
    rich_install()
    cappa.invoke(HttpFptCLI, version=__version__)
