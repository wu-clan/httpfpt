#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field
from typing_extensions import Literal

if TYPE_CHECKING:
    from httpfpt.enums.query_fetch_type import QueryFetchType

__all__ = [
    'CaseData',
    'CaseCacheData',
]


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
    proxies: dict[Literal['http', 'https', 'http://', 'https://'], AnyHttpUrl | None] | None = None


class Config(BaseModel):
    allure: ConfigAllureData
    request: ConfigRequestData
    module: str
    mark: list[str] | None = None


class StepsRequestData(BaseModel):
    method: Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    url: str
    params: dict | list[tuple] | bytes | None
    headers: dict | None
    cookies: dict | None = None
    body_type: Literal['form', 'x_form', 'binary', 'GraphQL', 'text', 'js', 'json', 'html', 'xml'] | None
    body: Any | None
    files: dict[str, str | list[str]] | None


class SetupTestCaseRequest(BaseModel):
    value: Any
    jsonpath: str = Field(pattern=r'^\$\.[a-zA-Z]+(?:\.[a-zA-Z]+)*$')  # $.xxx


class SetupTestCaseResponse(BaseModel):
    key: str
    jsonpath: str


class SetupTestCaseData(BaseModel):
    case_id: str
    request: list[SetupTestCaseRequest] | None = None
    response: list[SetupTestCaseResponse] | None = None


class SetupSqlData(BaseModel):
    key: str
    type: Literal['cache', 'env', 'global']
    sql: str
    fetch: QueryFetchType | None = None
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


class TeardownJsonAssertData(BaseModel):
    check: str | None = None
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
    value: Any
    jsonpath: str


class TeardownSqlAssertData(TeardownJsonAssertData):
    sql: str
    fetch: QueryFetchType | None = None


class TeardownJsonSchemaAssertData(BaseModel):
    check: str | None = None
    type: Literal['jsonschema']
    jsonschema: dict


class TeardownRegexAssertData(BaseModel):
    check: str | None = None
    type: Literal['re']
    pattern: str
    jsonpath: str


class StepsTearDownData(BaseModel):
    sql: str | SetupSqlData | None = None
    hook: str | None = None
    extract: TeardownExtractData | None = None
    assert_: (
        str
        | TeardownJsonAssertData
        | TeardownSqlAssertData
        | TeardownJsonSchemaAssertData
        | TeardownRegexAssertData
        | None
    ) = Field(None, alias='assert')
    wait_time: int | None = None


class Steps(BaseModel):
    name: str
    case_id: str
    description: str
    is_run: bool | dict | None = None
    mark: list[str] | None = None
    retry: int | None = None
    request: StepsRequestData
    setup: list[StepsSetUpData] | None = None
    teardown: list[StepsTearDownData] | None = None


class CaseData(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)

    config: Config
    test_steps: Steps | list[Steps]


class CaseCacheData(CaseData):
    filename: str | None = None
    file_hash: str | None = None
