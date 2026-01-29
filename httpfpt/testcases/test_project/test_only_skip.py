import pytest

from httpfpt.common.send_request import send_request
from httpfpt.utils.request.case_data_parse import get_testcase_data

ddt_data, ids = get_testcase_data(filename='only_skip.yml')


class TestOnlySkip:
    """OnlySkip"""

    @pytest.mark.parametrize('case_data', ddt_data, ids=ids)
    def test_only_skip(self, case_data):
        """only_skip"""
        send_request.send_request(case_data)
