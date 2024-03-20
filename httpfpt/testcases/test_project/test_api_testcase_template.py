#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import allure
import pytest

from httpfpt.common.send_request import send_request
from httpfpt.utils.request.case_data_parse import get_testcase_data

allure_data, ddt_data, ids = get_testcase_data(filename='api_testcase_template.yaml')


@allure.epic(allure_data['epic'])
@allure.feature(allure_data['feature'])
class TestApiTestcaseTemplate:
    """ApicaseTemplate"""

    @allure.story(allure_data['story'])
    @pytest.mark.parametrize('data', ddt_data, ids=ids)
    def test_api_testcase_template(self, data):
        """api_testcase_template"""
        send_request.send_request(data)
