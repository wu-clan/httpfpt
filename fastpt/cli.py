#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys
from typing import Optional, Tuple

import typer
from rich import print  # noqa

sys.path.append('..')

from fastpt.utils.case_auto_generator import auto_generate_test_cases  # noqa
from fastpt.utils.data_manage.openapi import SwaggerParser  # noqa
from fastpt.utils.data_manage.apifox import ApiFoxParser  # noqa

app = typer.Typer(rich_markup_mode='rich')


def get_version(version: bool):
    """
    获取版本号
    """
    if version:
        ver = open("./__init__.py", "rt").read()
        mob = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", ver, re.M)
        if mob:
            print('Fastpt', mob.group(1))
            raise typer.Exit()
        else:
            raise RuntimeError("Unable to find version string")


def generate_test_cases(generate: bool):
    """
    生成测试用例
    """
    if generate:
        typer.secho(
            '\n'
            'Warning: 此操作生成的测试用例是依赖测试数据文件而决定的,\n'
            '         如果你手动创建的测试用例与测试数据文件名称相吻合,\n'
            '         那么此操作将不能完全保证你的手动创建测试用例继续保留,\n'
            '         如果你依然执行此操作, 请谨慎选择重新生成所有测试用例。\n',
            fg='bright_yellow',
            bold=True
        )
        result = typer.confirm('⚠️ 是否重新生成所有测试用例?', default=False)
        try:
            if result:
                typer.secho('🔥 开始重新生成所有测试用例...', fg='cyan', bold=True)
                auto_generate_test_cases(rewrite=True)
            else:
                typer.secho('🔥 开始生成新测试用例...', fg='cyan', bold=True)
                auto_generate_test_cases()
        except Exception as e:
            typer.secho(f'❌ 自动生成测试用例失败: {e}', fg='red', bold=True)
            raise typer.Exit(1)
        else:
            raise typer.Exit()


def import_openapi_data(swagger: tuple):
    """
    导入 openapi 测试用例数据
    """
    typer.secho(
        '\n'
        'Warning: 如果现有文件名与导入文件名相同, 此命令目前会覆盖写入用例数据, 请谨慎操作。\n',
        fg='bright_yellow',
        bold=True
    )
    result = typer.confirm('⚠️ 确认执行此操作吗?', default=False)
    if result:
        typer.secho('🔥 开始导入 openapi 数据...', fg='cyan', bold=True)
        try:
            SwaggerParser().import_openapi_to_yaml(swagger[0], swagger[1])
        except Exception as e:
            typer.secho('❌ 导入 openapi 数据失败', fg='red', bold=True)
            raise e
        else:
            raise typer.Exit()
    else:
        raise typer.Abort()


def import_apifox_data(apifox: tuple):
    """
    导入 apifox 测试用例数据
    """
    typer.secho(
        '\n'
        'Warning: 如果现有文件名与导入文件名相同, 此命令目前会覆盖写入用例数据, 请谨慎操作。\n',
        fg='bright_yellow',
        bold=True
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
            raise typer.Exit()
    else:
        raise typer.Abort()


@app.command(epilog='Made by :beating_heart: null')
def main(
        _get_version: Optional[bool] = typer.Option(
            None,
            '--version',
            '-V',
            help='获取当前框架版本号',
            callback=get_version
        ),
        _generate_test_cases: Optional[bool] = typer.Option(
            None,
            '--generate-test-cases',
            '-gtc',
            help='自动生成测试用例',
            callback=generate_test_cases
        ),
        _import_openapi_data: Tuple[str, str] = typer.Option(
            (..., ...),
            '--import-openapi-data',
            '-iod',
            '-isd',
            show_default=False,
            metavar='<swagger/openapi, project>',
            help='导入 openapi / swagger 数据到 yaml 数据文件; 支持通过 json文件 / url链接 进行导入, project: 指定测试项目',
            callback=import_openapi_data
        ),
        _import_apifox_data: Tuple[str, str] = typer.Option(
            (..., ...),
            '--import-apifox-data',
            '-iad',
            show_default=False,
            metavar='<apifox, project>',
            help='导入 apifox 数据到 yaml 数据文件; 支持通过 json文件 进行导入, project: 指定测试项目',
            callback=import_apifox_data
        ),
):
    print('\n使用 --help 查看使用方法.\n')
    raise typer.Exit()


if __name__ == '__main__':
    app()
