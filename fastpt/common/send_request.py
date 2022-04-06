#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import json
import time
from typing import Union

import httpx
import requests
from httpx import Response as httpx_rq
from requests import Response as requests_rq

from fastpt.common.log import log
from fastpt.core import get_conf


class SendRequests:
    """ 发送请求 """

    def __init__(self, requestMethod: str = None):
        """
        :param requestMethod: 请求方式
        """
        self.requestMethod = requestMethod

    @staticmethod
    def __data(data) -> list:
        """
        :param data: 请求数据
        :return:
        """
        method = data["method"]
        url = data["url"]
        if data["params"] == "" or data["params"] is None:
            params = None
        else:
            params = eval(data["params"])
        if data["headers"] == "" or data["headers"] is None:
            headers = None
        else:
            headers = dict(data["headers"])
        if data["body"] == "" or data["body"] is None:
            body_data = None
        else:
            body_data = eval(data["body"])
        if data["body_type"] == "data":
            body = body_data
        elif data["body_type"] == "json":
            body = json.dumps(body_data)
        else:
            body = body_data
        return [method, url, params, headers, body]

    def __send_req(self, data) -> Union[httpx_rq, requests_rq]:
        """
        发送请求

        :param data: 请求数据
        :return: response
        """
        err = ['requests', 'httpx']
        if self.requestMethod not in err:
            raise ValueError(f'请求参数错误，仅 {err}')

        # 记录请求参数
        req_args = self.__data(data)
        req_method = req_args[0]
        req_url = req_args[1]
        req_params = req_args[2]
        req_headers = req_args[3]
        req_data = req_args[4]

        if self.requestMethod == 'requests':
            try:
                # 消除安全警告
                requests.packages.urllib3.disable_warnings()
                # 请求间隔
                time.sleep(get_conf.REQUEST_INTERVAL)
                rq = requests.session().request(method=req_method, url=req_url, params=req_params, headers=req_headers,
                                                data=req_data, timeout=get_conf.REQUEST_TIMEOUT,
                                                verify=get_conf.REQUEST_VERIFY)
                return rq
            except Exception as e:
                log.error(f'请求异常: \n {e}')
                raise e

        if self.requestMethod == 'httpx':
            try:
                # 请求间隔
                time.sleep(get_conf.REQUEST_INTERVAL)
                with httpx.Client(verify=get_conf.REQUEST_VERIFY, follow_redirects=True) as client:
                    rq = client.request(method=req_method, url=req_url, params=req_params, headers=req_headers,
                                        data=req_data, timeout=get_conf.REQUEST_TIMEOUT)
                    return rq
            except Exception as e:
                log.error(f'请求异常: \n {e}')
                raise e

    def send_requests(self, data) -> requests_rq:
        """
        通过 requests 发送请求

        :param data: 请求数据
        :return:
        """
        self._req_log(data)
        self.requestMethod = 'requests'
        return self.__send_req(data)

    def send_httpx(self, data) -> httpx_rq:
        """
        通过 httpx 发送请求

        :param data:
        :return:
        """
        self._req_log(data)
        self.requestMethod = 'httpx'
        return self.__send_req(data)

    @staticmethod
    def _req_log(data):
        log.info(f"正在调用的数据ID: --> {data['ID']}")
        log.info(f"请求 method: {data['method']}")
        log.info(f"请求 url: {data['url']}")
        log.info(f"请求 params: {data['params']}")
        log.info(f'请求 headers: {data["headers"]}')
        log.info(f"请求 body 类型：{data['body_type']}")
        log.info(f"请求 body：{data['body']}")


send_request = SendRequests()

__all__ = [
    'send_request'
]
