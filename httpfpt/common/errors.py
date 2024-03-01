#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class HttpFptErrorMixin:
    """HttpFpt错误基类"""

    def __init__(self, msg: str) -> None:
        self.msg = msg

    def __str__(self) -> str:
        return self.msg


class ConfigInitError(HttpFptErrorMixin, FileNotFoundError):
    """配置初始化错误"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class AuthError(HttpFptErrorMixin, ValueError):
    """认证错误"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class RequestDataParseError(HttpFptErrorMixin, ValueError):
    """请求数据解析错误"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class CorrelateTestCaseError(HttpFptErrorMixin, ValueError):
    """关联测试用例错误"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class SendRequestError(HttpFptErrorMixin, RuntimeError):
    """发送请求错误"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class JsonPathFindError(HttpFptErrorMixin, ValueError):
    """JsonPath查找错误"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class VariableError(HttpFptErrorMixin, ValueError):
    """变量错误"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class SQLSyntaxError(HttpFptErrorMixin, ValueError):
    """SQL语法错误"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class AssertSyntaxError(HttpFptErrorMixin, ValueError):
    """断言格式错误"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class AssertError(HttpFptErrorMixin, AssertionError):
    """断言错误"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)
