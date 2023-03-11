#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import NoReturn

from fastpt.common.log import log
from fastpt.core import get_conf


class LarkTalk:

    def __init__(self, content: dict):
        self.content = content

    def send(self) -> NoReturn:
        # 发送飞书消息
        try:
            import requests
            headers = {'Content-Type': 'application/json; charset=utf-8', 'Connection': 'close'}
            data = {
                "msg_type": "post",
                "content": {
                    "post": {
                        "zh_cn": {
                            "title": f"{get_conf.PROJECT_NAME} 自动化测试报告",
                            "content": [
                                [
                                    {
                                        "tag": "text",
                                        "text": f"👤 测试人员: {get_conf.TESTER_NAME}"
                                    }
                                ],
                                [
                                    {
                                        "tag": "text",
                                        "text": f"🤖 测试结果: {self.content['result']}"
                                    }
                                ],
                                [
                                    {
                                        "tag": "text",
                                        "text": f"✅ 通过用例: {self.content['passed']}"
                                    }
                                ],
                                [

                                    {
                                        "tag": "text",
                                        "text": f"🔧 失败用例: {self.content['failed']}"
                                    }
                                ],
                                [
                                    {
                                        "tag": "text",
                                        "text": f"❌ 错误用例: {self.content['error']}"
                                    }
                                ],
                                [

                                    {
                                        "tag": "text",
                                        "text": f"⚠️ 跳过用例: {self.content['skipped']}"
                                    }
                                ],
                                [
                                    {
                                        "tag": "text",
                                        "text": f"⌛ 开始时间: {self.content['started_time']}"
                                    }
                                ],
                                [
                                    {
                                        "tag": "text",
                                        "text": f"⏱️ 执行耗时: {self.content['elapsed']} s"
                                    }
                                ],
                                [
                                    {
                                        "tag": "a",
                                        "text": "➡️ 查看详情",
                                        "href": 'https://foryourself'
                                    }
                                ]
                            ]
                        }
                    }
                }
            }
            response = requests.session().post(
                url=get_conf.LARK_TALK_WEBHOOK,
                json=data,
                headers=headers,
                proxies=get_conf.LARK_TALK_PROXY
            )
            response.raise_for_status()
        except Exception as e:
            log.error(f'飞书消息发送异常: {e}')
        else:
            log.success('飞书消息发送成功')
