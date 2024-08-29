#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from httpfpt.common.send_request import send_request
from httpfpt.utils.request.case_data_parse import get_testcase_data

ddt_data, ids = get_testcase_data(filename='api_testcase_template.yaml')


class TestApiTestcaseTemplate:
    """ApicaseTemplate"""

    @pytest.mark.parametrize('case_data', ddt_data, ids=ids)
    def test_api_testcase_template(self, case_data):
        """api_testcase_template"""
        send_request.send_request(case_data)
