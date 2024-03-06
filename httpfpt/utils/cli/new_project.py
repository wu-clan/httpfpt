#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import shutil

import cappa


def create_new_project(start_project: tuple[str, str]) -> None:
    name = start_project[0]
    path = start_project[1]
    if path != '.':
        if not os.path.isdir(path):
            raise cappa.Exit(f'"{path}" is not a directory', code=1)
    project_path = os.path.join(path, name)
    if os.path.exists(project_path):
        raise cappa.Exit('The project directory is not empty', code=1)
    os.makedirs(project_path)
    shutil.copytree('./core', project_path, ignore=shutil.ignore_patterns('get_conf.py', 'path_conf.py'))
    shutil.copytree('./data', project_path)
    shutil.copytree('./testcases', project_path)
    shutil.copyfile('conftest.py', project_path)
    shutil.copyfile('pytest.ini', project_path)
    run_settings_path = os.path.join(project_path, 'core', 'conf.toml')
    init_tpl = f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from httpfpt import set_httpfpt_dir
from httpfpt import set_httpfpt_config

set_httpfpt_dir({project_path})
set_httpfpt_config({run_settings_path})
"""
    run_tpl = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from httpfpt import httpfpt_run


httpfpt_run()
"""
    with open(os.path.join(project_path, '__init__.py'), 'w', encoding='utf-8') as f:
        f.write(init_tpl)
    with open(os.path.join(project_path, 'run.py'), 'w', encoding='utf-8') as f:
        f.write(run_tpl)
