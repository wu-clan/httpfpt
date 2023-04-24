#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import allure
import pytest
from dirty_equals import IsInt

from fastpt.common.log import log


@allure.epic('demo')
@allure.feature('示例')
class TestDemo:
    """Demo"""

    @allure.story('简单输出')
    @pytest.mark.test_mark
    @pytest.mark.parametrize('a, b', [(1, 2)])
    def test_001(self, a, b):
        """测试001"""
        log.info("This is a demo's test")
        assert a != b

    @allure.story('xfall输出')
    @pytest.mark.xfail
    @pytest.mark.test_mark
    def test_002(self):
        """测试002"""
        log.info('这是一个框架xfail修饰测试')
        assert 1 == IsInt
