#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

import allure
import pytest

from fastpt.common.send_request import send_request
from fastpt.common.yaml_handler import read_yaml
from fastpt.core.get_conf import PROJECT_NAME
from fastpt.utils.request.case_data_file_parse import get_request_data
from fastpt.utils.request.ids_extract import get_ids

request_data = get_request_data(
    file_data=read_yaml(filename=os.sep.join([PROJECT_NAME, 'only_skip.yml'])),
    use_pydantic_verify=False
)
allure_text = request_data[0]['config']['allure']  # noqa
request_ids = get_ids(request_data)


@allure.epic(allure_text['epic'])
@allure.feature(allure_text['feature'])
class TestOnlySkip:

    @allure.story(allure_text['story'])
    @pytest.mark.parametrize('data', request_data, ids=request_ids)
    def test_only_skip(self, data):
        """ only_skip """
        send_request.send_request(data)
        