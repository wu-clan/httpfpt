#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from httpfpt.common.log import log
from httpfpt.core.get_conf import config


class LarkTalk:
    def __init__(self, content: dict):
        self.content = content

    def send(self) -> None:
        # 发送飞书消息
        try:
            import requests

            headers = {'Content-Type': 'application/json; charset=utf-8', 'Connection': 'close'}
            data = {
                'msg_type': 'post',
                'content': {
                    'post': {
                        'zh_cn': {
                            'title': config.TEST_REPORT_TITLE,
                            'content': [
                                [{'tag': 'text', 'text': f'👤 测试人员: {config.TESTER_NAME}'}],
                                [{'tag': 'text', 'text': f"🤖 测试结果: {self.content['result']}"}],
                                [{'tag': 'text', 'text': f"✅ 通过用例: {self.content['passed']}"}],
                                [{'tag': 'text', 'text': f"🔧 失败用例: {self.content['failed']}"}],
                                [{'tag': 'text', 'text': f"❌ 错误用例: {self.content['error']}"}],
                                [{'tag': 'text', 'text': f"⚠️ 跳过用例: {self.content['skipped']}"}],
                                [{'tag': 'text', 'text': f"⌛ 开始时间: {self.content['started_time']}"}],
                                [{'tag': 'text', 'text': f"⏱️ 执行耗时: {self.content['elapsed']} s"}],
                                [{'tag': 'a', 'text': '➡️ 查看详情', 'href': 'https://foryourself'}],
                            ],
                        }
                    }
                },
            }
            response = requests.session().post(
                url=config.LARK_TALK_WEBHOOK,
                json=data,
                headers=headers,
                proxies=config.LARK_TALK_PROXY,  # type: ignore
            )
            response.raise_for_status()
        except Exception as e:
            log.error(f'飞书消息发送异常: {e}')
        else:
            log.success('飞书消息发送成功')
