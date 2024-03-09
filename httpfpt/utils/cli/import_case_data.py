#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from rich.prompt import Confirm

from httpfpt.utils.data_manage.apifox import ApiFoxParser
from httpfpt.utils.data_manage.git_repo import GitRepoPaser
from httpfpt.utils.data_manage.openapi import SwaggerParser
from httpfpt.utils.rich_console import console


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
