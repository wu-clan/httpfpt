#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Optional, Union, Tuple, List, Dict

from pydantic import BaseModel, Field


class ConfigAllureData(BaseModel):
    epic: str
    feature: str
    story: str


class ConfigRequestData(BaseModel):
    env: str
    headers: Optional[dict] = None
    timeout: Optional[int] = None
    verify: Optional[bool] = None
    redirects: Optional[bool] = None
    proxies: Optional[dict] = None


class ConfigModuleData(BaseModel):
    module: str


class StepsCaseInfoData(BaseModel):
    name: str
    case_id: str
    description: str
    is_run: Union[bool, str, None] = None


class StepsRequestData(BaseModel):
    method: str
    url: str
    params: Union[dict, bytes, None] = None
    headers: dict
    data_type: str
    data: Union[dict, bytes, Tuple[list], None] = None
    files: Union[List[Dict[Union[list, str]]], None] = None


class StepsSetUpData(BaseModel):
    testcase: Union[str, list, None] = None
    sql: Optional[list] = None
    hook: Optional[list] = None
    wait_time: Optional[int] = None


class StepsTearDownData(BaseModel):
    sql: Optional[list] = None
    hook: Optional[list] = None
    extract: Optional[list] = None
    assert_: Union[str, list, None] = Field(None, alias='assert')
    wait_time: Optional[int] = None
