#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from httpfpt.common.send_request import send_request
from httpfpt.utils.request.case_data_parse import get_testcase_data

ddt_data, ids = get_testcase_data(filename='upload_file.json')


class TestUploadFile:
    """UploadFile"""

    @pytest.mark.parametrize('case_data', ddt_data, ids=ids)
    def test_upload_file(self, case_data):
        """upload_file"""
        send_request.send_request(case_data)
