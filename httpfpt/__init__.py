#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from httpfpt.core.get_conf import set_httpfpt_config as set_httpfpt_config
from httpfpt.core.path_conf import set_httpfpt_dir as set_httpfpt_dir
from httpfpt.run import run as httpfpt_run

__version__ = 'v0.5.1'

__all__ = [
    'set_httpfpt_config',
    'set_httpfpt_dir',
    'httpfpt_run',
]
