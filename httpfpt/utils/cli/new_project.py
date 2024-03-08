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
    if path != '.':
        if not os.path.isdir(path):
            raise cappa.Exit(f'\n❌ The "{path}" is not a directory', code=1)
    project_path = os.path.abspath(os.sep.join([path, name]))
    core_path = os.path.join(project_path, 'core')
    data_path = os.path.join(project_path, 'data')
    conftest_file = os.path.join(project_path, 'conftest.py')
    pytest_file = os.path.join(project_path, 'pytest.ini')
    if os.path.exists(project_path):
        raise cappa.Exit(f'\n❌ The "{name}" directory is not empty', code=1)
    os.makedirs(project_path)
    with import_path('httpfpt.core', '') as core_data:
        shutil.copytree(core_data, core_path, ignore=shutil.ignore_patterns('get_conf.py', 'path_conf.py'))
    with import_path('httpfpt.data', '') as case_data:
        shutil.copytree(case_data, data_path)
    with import_path('httpfpt', 'conftest.py') as conftest:
        shutil.copyfile(conftest, conftest_file)
    with import_path('httpfpt', 'pytest.ini') as pytest_ini:
        shutil.copyfile(pytest_ini, pytest_file)
    init_tpl = f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functools import wraps
from typing import Any, Callable

from httpfpt import set_httpfpt_dir

# Init setup
set_httpfpt_dir('{project_path}')


def ensure_httpfpt_setup(func: Callable) -> Any:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Callable:
        set_httpfpt_dir('{project_path}')
        return func(*args, **kwargs)

    return wrapper

"""
    run_tpl = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from httpfpt.run import run as httpfpt_run

httpfpt_run(testcase_generate=True)

"""
    with open(os.path.join(project_path, '__init__.py'), 'w', encoding='utf-8') as f:
        f.write(init_tpl)
    with open(os.path.join(project_path, 'run.py'), 'w', encoding='utf-8') as f:
        f.write(run_tpl)
    console.print(
        f'\n🎉 The project "{name}" has been created.'
        f'\n🌴 The project is located in the directory: [cyan]{project_path}[/]'
    )
