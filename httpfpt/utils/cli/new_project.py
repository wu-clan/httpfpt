#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import shutil

from importlib.resources import path as import_path

import cappa

from rich.prompt import Prompt

from httpfpt.utils.rich_console import console


def create_new_project() -> None:
    name = Prompt.ask('❓ Set your project a name', default='httpfpt_project')
    path = Prompt.ask('❓ Set your project path (relative or absolute path, which automatically parses.)', default='.')
    console.print('\n⏳ The project is being created automatically...')
    if path != '.':
        if not os.path.isdir(path):
            raise cappa.Exit(f'\n❌ The "{path}" is not a directory', code=1)
    # TODO: 添加 rich 创建过程进度打印
    project_path = os.path.abspath(os.sep.join([path, name]))
    core_path = os.path.join(project_path, 'core')
    data_path = os.path.join(project_path, 'data')
    init_file = os.path.join(project_path, '__init__.py')
    conftest_file = os.path.join(project_path, 'conftest.py')
    pytest_file = os.path.join(project_path, 'pytest.ini')
    if os.path.exists(project_path):
        raise cappa.Exit(f'\n❌ The "{name}" directory is not empty', code=1)
    os.makedirs(project_path)
    with import_path('httpfpt.core', '') as core_data:
        patterns = ['__init__.py', 'get_conf.py', 'path_conf.py']
        shutil.copytree(core_data, core_path, ignore=shutil.ignore_patterns(*patterns))
    with import_path('httpfpt.data', '') as case_data:
        shutil.copytree(case_data, data_path)
    with import_path('httpfpt', '__init__.py') as pytest_init:
        shutil.copyfile(pytest_init, init_file)
    with import_path('httpfpt', 'conftest.py') as conftest:
        shutil.copyfile(conftest, conftest_file)
    with import_path('httpfpt', 'pytest.ini') as pytest_ini:
        shutil.copyfile(pytest_ini, pytest_file)
    run_tpl = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from httpfpt.run import run as httpfpt_run

httpfpt_run(testcase_generate=True)

"""
    with open(os.path.join(project_path, 'run.py'), 'w', encoding='utf-8') as f:
        f.write(run_tpl)
    console.print(
        f'\n🎉 The project "{name}" has been created.'
        f'\n🌴 The project is located in the directory: [cyan]{project_path}[/]'
        f'\n⚠️ Before accessing HTTPFPT, be sure to set the environment variable '
        f'[yellow]HTTPFPT_PROJECT_PATH[/] to the current project directory'
        f'\n   Windows: setx HTTPFPT_PROJECT_PATH "{project_path}"'
        f'\n   Unix: vim ~/.bashrc'
        f'\n\t export PATH=$PATH:{project_path}'
    )
