#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Dict, List, Literal

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field

__all__ = ['CaseData']


class ConfigAllureData(BaseModel):
    epic: str
    feature: str
    story: str
    severity: str | None = None


class ConfigRequestData(BaseModel):
    env: str
    headers: dict | None = None
    timeout: int | None = Field(None, ge=0)
    verify: bool | None = None
    redirects: bool | None = None
    proxies: Dict[Literal['http', 'https', 'http://', 'https://'], AnyHttpUrl | None] | None = None


class Config(BaseModel):
    allure: ConfigAllureData
    request: ConfigRequestData
    module: str


class StepsRequestData(BaseModel):
    method: Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    url: str
    params: dict | List[tuple] | bytes | None
    headers: dict | None
    body_type: Literal['form', 'x_form', 'binary', 'GraphQL', 'text', 'js', 'json', 'html', 'xml'] | None
    body: Any | None
    files: Dict[str, str | List[str]] | None
    retry: int | None = None


class SetupTestCaseData(BaseModel):
    case_id: str
    key: str
    jsonpath: str


class SetupSqlData(BaseModel):
    key: str
    type: Literal['cache', 'wnv', 'global']
    sql: str
    jsonpath: str


class StepsSetUpData(BaseModel):
    testcase: str | SetupTestCaseData | None = None
    sql: str | SetupSqlData | None = None
    hook: str | None = None
    wait_time: int | None = None


class TeardownExtractData(BaseModel):
    key: str
    type: str
    jsonpath: str


class TeardownAssertData(BaseModel):
    check: str | None = None
    value: Any
    type: Literal[
        'eq',
        'not_eq',
        'gt',
        'ge',
        'lt',
        'le',
        'str_eq',
        'len_eq',
        'not_len_eq',
        'len_lt',
        'len_le',
        'len_gt',
        'len_ge',
        'contains',
        'not_contains',
        'startswith',
        'endswith',
    ]
    jsonpath: str


class StepsTearDownData(BaseModel):
    sql: str | SetupSqlData | None = None
    hook: str | None = None
    extract: TeardownExtractData | None = None
    assert_: str | TeardownAssertData | None = Field(None, alias='assert')
    wait_time: int | None = None


class Steps(BaseModel):
    name: str
    case_id: str
    description: str
    is_run: bool | dict | None = None
    retry: int | None = None
    request: StepsRequestData
    setup: List[StepsSetUpData] | None = None
    teardown: List[StepsTearDownData] | None = None


class CaseData(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)

    config: Config
    test_steps: Steps | List[Steps]
    filename: str | None = None
    file_hash: str | None = None
