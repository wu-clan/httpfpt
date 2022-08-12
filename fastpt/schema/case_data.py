#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Optional, Union, Tuple, List, Dict, Literal

from pydantic import BaseModel, Field, validator, AnyHttpUrl


class _ConfigAllureData(BaseModel):
    epic: str
    feature: str
    story: str

    @validator('*')
    def check_allure_type(cls, v):
        if not isinstance(v, str):
            raise ValueError(f'测试用例数据解析失败, 参数 config:allure:{v} 不是有效的 str 类型')
        return v


class _ConfigRequest(BaseModel):
    env: str
    headers: Optional[dict] = None
    timeout: Optional[int] = None
    verify: Optional[bool] = None
    redirects: Optional[bool] = None
    proxies: Union[Dict[Union[Literal['requests', 'httpx']], Dict[
        Literal['http', 'https', 'http://', 'https://'], Union[AnyHttpUrl, None]]]] = None  # noqa


class Config(BaseModel):
    allure: _ConfigAllureData
    request: _ConfigRequest
    module: str


class _StepsRequestData(BaseModel):
    method: str
    url: str
    params: Union[dict, bytes, None] = ...
    headers: Optional[dict] = ...
    data_type: Optional[str] = ...
    data: Union[dict, bytes, Tuple[list], None] = ...
    files: Union[Dict[str, Union[List[str], str]], None] = ...

    @validator('headers')
    def check_headers(cls, v):
        if v is not None:
            if not isinstance(v, dict):
                raise ValueError('请求数据解析失败, 参数 test_steps:request:headers 格式错误, 必须为 dict 类型')


class _StepsSetUpData(BaseModel):
    testcase: Union[List[Union[dict, str]], None] = None
    sql: Union[List[Union[dict, str]], None] = None
    hook: Optional[List[str]] = None
    wait_time: Optional[int] = None


class _StepsTearDownData(BaseModel):
    sql: Union[List[Union[dict, str]], None] = None
    hook: Optional[List[str]] = None
    extract: Optional[List[dict]] = None
    assert_: Union[List[Union[dict, str]], str, None] = Field(None, alias='assert')
    wait_time: Optional[int] = None


class Steps(BaseModel):
    name: str
    case_id: str
    description: str
    is_run: Union[bool, str, None] = ...
    request: _StepsRequestData
    setup: Optional[_StepsSetUpData] = None
    teardown: Optional[_StepsTearDownData] = None


class CaseData(BaseModel):
    config: Config
    test_steps: Steps
