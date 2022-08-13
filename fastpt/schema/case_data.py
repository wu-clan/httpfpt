#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Optional, Union, Tuple, List, Dict, Any, Literal

from pydantic import BaseModel, Field, AnyHttpUrl


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
    proxies: Union[Dict[Union[Literal['requests', 'httpx']], Dict[
        Literal['http', 'https', 'http://', 'https://'], Union[AnyHttpUrl, None]]]] = None  # noqa


class Config(BaseModel):
    allure: ConfigAllureData
    request: ConfigRequestData
    module: str


class StepsRequestData(BaseModel):
    method: str
    url: str
    params: Union[dict, bytes, None] = ...
    headers: Optional[dict] = ...
    data_type: Optional[str] = ...
    data: Union[dict, bytes, Tuple[list], None] = ...
    files: Union[Dict[str, Union[List[str], str]], None] = ...


class SetupTestCaseData(BaseModel):
    case_id: str
    key: str
    jsonpath: str


class SetupSqlData(BaseModel):
    key: str
    set_type: str
    sql: str
    jsonpath: str


class StepsSetUpData(BaseModel):
    testcase: Union[List[Union[SetupTestCaseData, str]], None] = None
    sql: Union[List[Union[SetupSqlData, str]], None] = None
    hooks: Optional[List[str]] = None
    wait_time: Optional[int] = None


class TeardownExtractData(BaseModel):
    key: str
    set_type: str
    jsonpath: str


class TeardownAssertData(BaseModel):
    check: str
    value: Any
    type: str
    jsonpath: str


class StepsTearDownData(BaseModel):
    sql: Union[List[Union[SetupSqlData, str]], None] = None
    hooks: Optional[List[str]] = None
    extract: Optional[List[TeardownExtractData]] = None
    assert_: Union[List[Union[TeardownAssertData, str]], str, None] = Field(None, alias='assert')
    wait_time: Optional[int] = None


class Steps(BaseModel):
    name: str
    case_id: str
    description: str
    is_run: Union[bool, str, None] = ...
    request: StepsRequestData
    setup: Optional[StepsSetUpData] = None
    teardown: Optional[StepsTearDownData] = None


class CaseData(BaseModel):
    """
    暂不使用此类直接对请求参数做快速校验, 考虑到后期是否对 excel 数据提供支持,
    如果提供, 那么使用此校验器将会造成 excel 数据错误判断, 除非在 excel 请求数据转化时直接格式化参数请求格式,
    同时更新和移除请求参数解析中不必要的对 excel 请求数据的二次解析(在此校验器发生之前专门为 excel 请求数据提供的设计)
    """
    config: Config
    test_steps: Steps
