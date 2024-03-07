#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import sys

from dataclasses import dataclass

import cappa

from cappa import Subcommands
from rich.traceback import install as rich_install
from typing_extensions import Annotated

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from httpfpt.utils.cli.about_testcase import generate_testcases, testcase_data_verify
from httpfpt.utils.cli.import_case_data import (
    import_apifox_case_data,
    import_git_case_data,
    import_har_case_data,
    import_jmeter_case_data,
    import_openapi_case_data,
    import_postman_case_data,
)
from httpfpt.utils.cli.new_project import create_new_project
from httpfpt.utils.cli.version import get_version


@cappa.command(name='httpfpt-cli')
@dataclass
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
    start_project: Annotated[
        bool,
        cappa.Arg(
            value_name='<PROJECT NAME, PROJECT PATH>',
            short=False,
            long='--startproject',
            default=False,
            help='Create a new project.',
            required=False,
        ),
    ]
    subcmd: Subcommands[TestCaseCLI | ImportCLI | None] = None

    def __call__(self) -> None:
        if self.version:
            get_version()
        if self.start_project:
            create_new_project()


@cappa.command(name='testcase', help='Test case tools.')
@dataclass
class TestCaseCLI:
    data_verify: Annotated[
        str,
        cappa.Arg(
            value_name='<FILENAME / ALL>',
            short='-dv',
            long=True,
            default='',
            help='验证测试数据结构；当指定文件（文件名/完整路径）时, 仅验证指定文件, 当指定 "all" 时, 验证所有文件.',
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
            short='-io',
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
            short='-ia',
            long='--import-apifox',
            default=(),
            help='Beta: 导入 apifox 数据到 yaml 数据文件; 支持 json 文件导入, 需要指定 project 项目名.',
            required=False,
        ),
    ]
    har: Annotated[
        tuple[str, str],
        cappa.Arg(
            short='-ih',
            long='--import-har',
            default=(),
            help='TODO: Not started yet.',
            required=False,
        ),
    ]
    jmeter: Annotated[
        tuple[str, str],
        cappa.Arg(
            short='-ij',
            long='--import-jmeter',
            default=(),
            help='TODO: Not started yet.',
            required=False,
        ),
    ]
    postman: Annotated[
        tuple[str, str],
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


def cappa_invoke() -> None:
    """cli 执行程序"""
    rich_install()
    cappa.invoke(HttpFptCLI)


if __name__ == '__main__':
    cappa_invoke()
