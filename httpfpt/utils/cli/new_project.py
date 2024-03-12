#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import platform
import shutil

from importlib.resources import path as import_path
from time import sleep

import cappa

from rich.prompt import Prompt
from rich.syntax import Syntax

from httpfpt.utils.rich_console import console


def create_new_project() -> None:
    name = Prompt.ask('❓ Set your project a name', default='httpfpt_project')
    path = Prompt.ask('❓ Set your project path (relative or absolute path, which automatically parses.)', default='.')
    if path != '.':
        if not os.path.isdir(path):
            raise cappa.Exit(f'\n❌ The "{path}" is not a directory', code=1)
    with console.status('[bold green]The project is being created...[/]'):
        console.print(end='\n')
        sleep(2)

        project_path = os.path.abspath(os.sep.join([path, name]))
        if os.path.exists(project_path):
            raise cappa.Exit(f'\n❌ The "{project_path}" directory is not empty', code=1)
        os.makedirs(project_path)
        console.print('📁 Created the project folder')
        sleep(2)

        core_path = os.path.join(project_path, 'core')
        with import_path('httpfpt.core', '') as core_data:
            patterns = ['__init__.py', 'get_conf.py', 'path_conf.py']
            shutil.copytree(core_data, core_path, ignore=shutil.ignore_patterns(*patterns))
            console.print('📄 Created core files')
            sleep(2)

        data_path = os.path.join(project_path, 'data')
        with import_path('httpfpt.data', '') as case_data:
            shutil.copytree(case_data, data_path)
            console.print('📄 Created case data samples')
            sleep(2)

        init_file = os.path.join(project_path, '__init__.py')
        with import_path('httpfpt', '__init__.py') as pytest_init:
            shutil.copyfile(pytest_init, init_file)

        conftest_file = os.path.join(project_path, 'conftest.py')
        with import_path('httpfpt', 'conftest.py') as conftest:
            shutil.copyfile(conftest, conftest_file)
            console.print('📄 Created pytest conftest')
            sleep(1)

        pytest_file = os.path.join(project_path, 'pytest.ini')
        with import_path('httpfpt', 'pytest.ini') as pytest_ini:
            shutil.copyfile(pytest_ini, pytest_file)
            console.print('📄 Created pytest ini')
            sleep(1)

        run_tpl = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from httpfpt.run import run as httpfpt_run

httpfpt_run(testcase_generate=True)

"""
        with open(os.path.join(project_path, 'run.py'), 'w', encoding='utf-8') as f:
            f.write(run_tpl)
            console.print('📄 Created run pytest file')

    console.print(
        f'\n🎉 The project <{name}> has been created.'
        f'\n🌳 The project is located in the directory: [cyan]{project_path}[/]'
        f'\n⚠️ Before accessing HTTPFPT, be sure to set the environment variable '
        '[yellow]HTTPFPT_PROJECT_PATH[/] to the current project directory',
        end='\n\n'
    )
    if platform.system().lower() == 'windows':
        env_var_cmd = f"""
# Windows
> setx HTTPFPT_PROJECT_PATH "{project_path}"
        """
    else:
        env_var_cmd = f"""
# Unix
> vim ~/.bashrc
> export PATH=$PATH:{project_path}
        """
    console.print(Syntax(env_var_cmd, 'shell', line_numbers=True))
