#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import allure
import pytest

from httpfpt.common.send_request import send_request
from httpfpt.utils.request.case_data_parse import get_request_data
from httpfpt.utils.request.ids_extract import get_ids

request_data = get_request_data(filename='upload_file.yaml')
allure_text = request_data[0]['config']['allure']
request_ids = get_ids(request_data)


@allure.epic(allure_text['epic'])
@allure.feature(allure_text['feature'])
class TestUploadFile:
    """UploadFile"""

    @allure.story(allure_text['story'])
    @pytest.mark.parametrize('data', request_data, ids=request_ids)
    def test_upload_file(self, data):
        """upload_file"""
        send_request.send_request(data)
