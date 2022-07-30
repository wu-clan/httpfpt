#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dotenv


def get_env_dict(filepath: str) -> dict:
    dotenv.find_dotenv(filepath, raise_error_if_not_found=True)
    env_dict = dict(dotenv.dotenv_values(filepath))
    return env_dict
