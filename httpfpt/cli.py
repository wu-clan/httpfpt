#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys
from typing import Optional, Tuple

import typer
from pydantic import ValidationError
from rich import print
from typing_extensions import Annotated

sys.path.append('..')

from httpfpt.common.yaml_handler import read_yaml
from httpfpt.schemas.case_data import CaseData
from httpfpt.utils.file_control import search_all_case_yaml_files
from httpfpt.utils.case_auto_generator import auto_generate_testcases
from httpfpt.utils.data_manage.openapi import SwaggerParser
from httpfpt.utils.data_manage.apifox import ApiFoxParser
from httpfpt.utils.data_manage.git_repo import GitRepoPaser

app = typer.Typer(add_completion=False, epilog='Made by :beating_heart: wu-clan', rich_markup_mode='rich')


def get_version(version: bool) -> None:
    """获取版本号"""
    if version:
        ver = open('./__init__.py', 'rt').read()
        mob = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", ver, re.M)
        if mob:
            print('Fastpt', mob.group(1))
            raise typer.Exit()
        else:
            raise RuntimeError('未查询到版本号')


def testcase_date_verify(verify: str) -> None:
    """测试数据验证"""
    msg: str = ''
    try:
        count: int = 0
        if verify.lower() == 'all':
            typer.secho('🔥 开始验证所有测试数据结构...', fg='cyan', bold=True)
            file_list = search_all_case_yaml_files()
            for file in file_list:
                file_data = read_yaml(None, filename=file)
                CaseData.model_validate(file_data, strict=True)
        else:
            typer.secho(f'🔥 开始验证 {verify} 测试数据结构...', fg='cyan', bold=True)
            file_data = read_yaml(None, filename=verify)
            CaseData.model_validate(file_data, strict=True)
    except ValidationError as e:
        count = e.error_count()
        msg += str(e)
    except Exception as e:
        typer.secho(f'❌ 验证测试数据 {verify} 结构失败: {e}', fg='red', bold=True)
        raise typer.Exit(1)
    if count > 0:
        typer.secho(f'❌ 验证测试数据 {verify} 结构失败: {msg}', fg='red', bold=True)
        raise typer.Exit(1)
    else:
        typer.secho('✅ 验证测试数据结构成功', fg='green', bold=True)


def generate_testcases(generate: bool) -> None:
    """生成测试用例"""
    if generate:
        typer.secho(
            '\n'
            'Warning: 此操作生成的测试用例是依赖测试数据文件而决定的,\n'
            '         如果你手动创建的测试用例与测试数据文件名称相吻合,\n'
            '         那么此操作将不能完全保证你的手动创建测试用例继续保留,\n'
            '         如果你依然执行此操作, 请谨慎选择重新生成所有测试用例。\n',
            fg='bright_yellow',
            bold=True,
        )
        result = typer.confirm('⚠️ 是否重新生成所有测试用例?', default=False)
        try:
            if result:
                typer.secho('🔥 开始重新生成所有测试用例...', fg='cyan', bold=True)
                auto_generate_testcases(rewrite=True)
            else:
                typer.secho('🔥 开始生成新测试用例...', fg='cyan', bold=True)
                auto_generate_testcases()
        except Exception as e:
            typer.secho(f'❌ 自动生成测试用例失败: {e}', fg='red', bold=True)
            raise typer.Exit(1)


def import_openapi_test_data(openapi: tuple) -> None:
    """导入 openapi 测试用例数据"""
    typer.secho(f'正在导入测试用例数据到项目: {openapi[1]}', fg='bright_yellow', bold=True)
    result = typer.confirm('确认执行此操作吗?', default=False)
    if result:
        typer.secho('🔥 开始导入 openapi 数据...', fg='cyan', bold=True)
        try:
            SwaggerParser().import_openapi_to_yaml(openapi[0], openapi[1])
        except Exception as e:
            typer.secho('❌ 导入 openapi 数据失败', fg='red', bold=True)
            raise e
    else:
        raise typer.Abort()


def import_apifox_test_data(apifox: tuple) -> None:
    """导入 apifox 测试用例数据"""
    typer.secho(
        """
        Beta: 此命令目前处于测试阶段, 请谨慎使用。
        Warning: 如果现有文件名与导入文件名相同, 此命令目前会覆盖写入用例数据, 请谨慎操作。
        """,
        fg='bright_yellow',
        bold=True,
    )
    result = typer.confirm('⚠️ 确认执行此操作吗?', default=False)
    if result:
        typer.secho('🔥 开始导入 apifox 数据...', fg='cyan', bold=True)
        try:
            ApiFoxParser().import_apifox_to_yaml(apifox[0], apifox[1])
        except Exception as e:
            typer.secho('❌ 导入 apifox 数据失败:', fg='red', bold=True)
            raise e
    else:
        raise typer.Abort()


def import_har_test_data(har: tuple) -> None:
    """导入 har 测试用例数据"""
    pass


def import_jmeter_test_data(jmeter: tuple) -> None:
    """导入 jmeter 测试用例数据"""
    pass


def import_postman_test_data(postman: tuple) -> None:
    """导入 postman 测试用例数据"""
    pass


def import_git_case_data(src: str) -> None:
    """导入 git 仓库测试数据"""
    typer.secho(f'正在导入 git 仓库测试数据到本地: {src}', fg='bright_yellow', bold=True)
    typer.secho('🔥 开始导入 git 仓库测试数据...', fg='cyan', bold=True)
    try:
        GitRepoPaser.import_git_to_local(src)
    except Exception as e:
        typer.secho(f'❌ 导入 git 仓库测试数据失败: {e}', fg='red', bold=True)
        raise e


@app.callback(name='version')
def callback(
    _get_version: Optional[bool] = typer.Option(None, '--version', '-V', help='打印版本号', callback=get_version),
) -> None:
    pass


@app.command('testcase', help='测试用例相关操作')
def testcase(
    _testcase_date_verify: Annotated[
        str,
        typer.Option(
            '--testcase-date-verify',
            '-tdv',
            metavar='<FILENAME / ALL>',
            show_default=False,
            help='验证测试数据结构, 当指定文件名时, 验证指定文件, 当指定 "all" 时, 验证所有文件',
            callback=testcase_date_verify,
        ),
    ],
    _generate_testcases: Annotated[
        Optional[bool],
        typer.Option('--generate-testcases', '-gt', help='自动生成测试用例', callback=generate_testcases),
    ] = None,
) -> None:
    pass


@app.command('import', help='导入测试用例数据')
def import_testcase_data(
    _import_openapi_testcase_data: Annotated[
        Tuple[str, str],
        typer.Option(
            '--import-openapi-testcase-data',
            '-io',
            '-is',
            show_default=False,
            metavar='<OPENAPI JSONFILE / URL, PROJECT>',
            help='导入 openapi / swagger 数据到 yaml 数据文件; 通过 json_file / url 导入; project: 指定项目名',
            callback=import_openapi_test_data,
        ),
    ],
    _import_apifox_testcase_data: Annotated[
        Tuple[str, str],
        typer.Option(
            '--import-apifox-testcase-data',
            '-ia',
            show_default=False,
            metavar='<APIFOX JSONFILE, PROJECT>',
            help='Beta: 导入 apifox 数据到 yaml 数据文件; 通过 json_file 导入; project: 指定项目名',
            callback=import_apifox_test_data,
        ),
    ],
    _import_har_testcase_data: Annotated[
        Tuple[str, str],
        typer.Option(
            '--import-har-testcase-data',
            '-ih',
            show_default=False,
            help='TODO: Not started yet',
            callback=import_har_test_data,
        ),
    ],
    _import_jmeter_testcase_data: Annotated[
        Tuple[str, str],
        typer.Option(
            '--import-jmeter-testcase-data',
            '-ij',
            show_default=False,
            help='TODO: Not started yet',
            callback=import_jmeter_test_data,
        ),
    ],
    _import_postman_testcase_data: Annotated[
        Tuple[str, str],
        typer.Option(
            '--import-postman-testcase-data',
            '-ipm',
            show_default=False,
            help='TODO: Not started yet',
            callback=import_postman_test_data,
        ),
    ],
    _import_git_repo_testcase_data: Annotated[
        str,
        typer.Option(
            '--import-git-repo-testcase-data',
            '-igr',
            show_default=False,
            help='导入 git 仓库测试数据到本地',
            callback=import_git_case_data,
        ),
    ],
) -> None:
    pass


if __name__ == '__main__':
    app()
