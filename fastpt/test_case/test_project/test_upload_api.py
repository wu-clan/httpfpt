#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import allure
import pytest

from fastpt.common.send_request import send_request
from fastpt.common.yaml_handler import read_yaml
from fastpt.utils.request.file_data_parse import get_request_data
from fastpt.utils.request.ids_extract import get_ids

request_data = get_request_data(read_yaml(filename='upload_file.yaml'))


@allure.epic(request_data[0]['config']['allure']['epic'])
@allure.feature(request_data[0]['config']['allure']['feature'])
class TestUpload:
    """ Upload """

    request_ids = get_ids(request_data)

    @allure.story(request_data[0]['config']['allure']['story'])
    @pytest.mark.test_api
    @pytest.mark.parametrize('data', request_data, ids=request_ids)
    def test_004(self, data):
        """ {0} """ .format(data['test_steps']['description'])
        send_request.send_request(data)
