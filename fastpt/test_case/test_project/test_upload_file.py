#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from pathlib import Path

import allure
import pytest

from fastpt.common.send_request import send_request
from fastpt.common.yaml_handler import read_yaml
from fastpt.utils.request.file_data_parse import get_request_data
from fastpt.utils.request.ids_extract import get_ids

request_data = get_request_data(read_yaml(filename=os.sep.join(Path(r'test_project\upload_file.yaml').parts)))
allure_text = request_data[0]['config']['allure']
request_ids = get_ids(request_data)


@allure.epic(allure_text['epic'])
@allure.feature(allure_text['feature'])
class TestUploadFile:

    @allure.story(allure_text['story'])
    # @pytest.mark.???
    @pytest.mark.parametrize('data', request_data, ids=request_ids)
    def test_upload_file(self, data):
        """ {0} """.format(data['test_steps']['description'])
        send_request.send_request(data)
        