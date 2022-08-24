#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys
from typing import Optional

import typer
from rich import print  # noqa

sys.path.append('..')

from fastpt.utils.case_auto_generator import auto_generate_test_cases
from fastpt.utils.data_manage.openapi import SwaggerParser

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
            print(f'❌ 自动生成测试用例失败: {e}')
            raise typer.Exit(1)
        else:
            raise typer.Exit()


def import_openapi_cases(
        ctx: typer.CallbackParam,
        openapi: str = typer.Argument(..., help='openapi url/openapi file'),
        project: Optional[str] = typer.Argument(None, help='指定导入项目，默认使用 conf 配置')):
    """
    导入 openapi 测试用例
    """
    typer.secho('🔥 开始导入 openapi 测试用例...', fg='cyan', bold=True)
    try:
        SwaggerParser().import_openapi_to_yaml(openapi, project)
    except Exception as e:
        print(f'❌ 导入 openapi 测试用例失败: {e}')
        raise typer.Exit(1)
    else:
        raise typer.Exit()


@app.command(epilog='Made by :beating_heart: null')
def main(
        _get_version: Optional[bool] = typer.Option(
            None,
            '--version',
            '-V',
            help='获取当前版本',
            callback=get_version
        ),
        _generate_test_cases: Optional[bool] = typer.Option(
            None,
            '--generate-test-cases',
            '-gtc',
            help='生成测试用例',
            callback=generate_test_cases
        ),
        # todo
        _import_openapi_cases: str = typer.Option(
            ...,
            '--import-openapi_case',
            '-ioc',
            help='导入 openapi 测试用例',
            callback=import_openapi_cases
        )
):
    print('\n使用 --help 查看使用方法.\n')
    raise typer.Exit()


if __name__ == '__main__':
    app()
