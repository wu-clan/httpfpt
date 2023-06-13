#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Optional, Union, Tuple, List, Dict, Any, Literal

from pydantic import BaseModel, Field, AnyHttpUrl


class ConfigAllureData(BaseModel):
    epic: str
    feature: str
    story: str
    severity: Optional[str] = None


class ConfigRequestData(BaseModel):
    env: str
    headers: Optional[dict] = None
    timeout: Optional[int] = Field(None, ge=0)
    verify: Optional[bool] = None
    redirects: Optional[bool] = None
    proxies: Optional[Union[Dict[Literal['http', 'https', 'http://', 'https://'], Union[AnyHttpUrl, None]]]] = None


class Config(BaseModel):
    allure: ConfigAllureData
    request: ConfigRequestData
    module: str


class StepsRequestData(BaseModel):
    method: str
    url: str
    params: Union[dict, bytes, None] = ...
    headers: Optional[dict] = ...
    body_type: Optional[str] = ...
    body: Union[dict, bytes, Tuple[list], None] = ...
    files: Union[Dict[str, Union[str, List[str]]], None] = ...


class SetupTestCaseData(BaseModel):
    case_id: str
    key: str
    jsonpath: str


class SetupSqlData(BaseModel):
    key: str
    type: str
    sql: str
    jsonpath: str


class StepsSetUpData(BaseModel):
    testcase: Optional[Union[List[Union[str, SetupTestCaseData]]]] = None
    sql: Optional[Union[List[Union[str, SetupSqlData]]]] = None
    hooks: Optional[List[str]] = None
    wait_time: Optional[int] = None


class TeardownExtractData(BaseModel):
    key: str
    type: str
    jsonpath: str


class TeardownAssertData(BaseModel):
    # check: Optional[str] = None
    check: str
    value: Any
    type: str
    jsonpath: str


class StepsTearDownData(BaseModel):
    sql: Optional[Union[List[Union[str, SetupSqlData]]]] = None
    hooks: Optional[List[str]] = None
    extract: Optional[List[TeardownExtractData]] = None
    assert_: Optional[Union[str, List[str], List[TeardownAssertData]]] = Field(None, alias='assert')
    wait_time: Optional[int] = None


class Steps(BaseModel):
    name: str
    case_id: str
    description: str
    is_run: Union[bool, dict, None] = ...
    request: StepsRequestData
    setup: Optional[StepsSetUpData] = None
    teardown: Optional[StepsTearDownData] = None


class CaseData(BaseModel):
    config: Config
    test_steps: Union[Steps, List[Steps]]
