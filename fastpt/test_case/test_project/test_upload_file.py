#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

import allure
import pytest

from fastpt.common.send_request import send_request
from fastpt.common.yaml_handler import read_yaml
from fastpt.core.get_conf import PROJECT_NAME
from fastpt.utils.request.file_data_parse import get_request_data
from fastpt.utils.request.ids_extract import get_ids

request_data = get_request_data(read_yaml(filename=os.sep.join([PROJECT_NAME, 'upload_file.yaml'])))
allure_text = request_data[0]['config']['allure']
request_ids = get_ids(request_data)


@allure.epic(allure_text['epic'])
@allure.feature(allure_text['feature'])
class TestUploadFile:

    @allure.story(allure_text['story'])
    # @pytest.mark.???
    @pytest.mark.parametrize('data', request_data, ids=request_ids)
    def test_upload_file(self, data):
        """ {0} """.format(data['test_steps']['description'] or '未知')
        send_request.send_request(data)
        