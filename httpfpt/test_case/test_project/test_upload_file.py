#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

import allure
import pytest

from httpfpt.common.send_request import send_request
from httpfpt.common.yaml_handler import read_yaml
from httpfpt.core.get_conf import PROJECT_NAME
from httpfpt.utils.request.case_data_file_parse import get_request_data
from httpfpt.utils.request.ids_extract import get_ids

request_data = get_request_data(
    file_data=read_yaml(filename=os.sep.join([PROJECT_NAME, 'upload_file.yaml'])), use_pydantic_verify=True
)
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
