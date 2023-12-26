#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from httpfpt.common.log import log
from httpfpt.core.get_conf import config


class DingTalk:
    def __init__(self, content: dict):
        self.content = content

    def send(self) -> None:
        try:
            import requests

            headers = {'Content-Type': 'application/json; charset=utf-8', 'Connection': 'close'}
            data = {
                'msgtype': 'markdown',
                'markdown': {
                    'title': config.TEST_REPORT_TITLE,
                    'text': f"> ## {config.PROJECT_NAME} 自动化测试报告\n\n"
                    f"> 👤 测试人员: {config.TESTER_NAME}\n\n"
                    f"> 🤖 测试结果: {self.content['result']}\n\n"
                    f"> ✅ 通过用例: {self.content['passed']}\n\n"
                    f"> 🔧 失败用例: {self.content['failed']}\n\n"
                    f"> ❌ 错误用例: {self.content['error']}\n\n"
                    f"> ⚠️ 跳过用例: {self.content['skipped']}\n\n"
                    f"> ⌛ 开始时间: {self.content['started_time']}\n\n"
                    f"> ⏱️ 执行耗时: {self.content['elapsed']} s\n\n"
                    f"> ➡️ [查看详情](https://foryourself)",
                },
            }
            response = requests.session().post(
                url=config.DING_TALK_WEBHOOK,
                json=data,
                headers=headers,
                proxies=config.DING_TALK_PROXY,  # type: ignore
            )
            response.raise_for_status()
        except Exception as e:
            log.error(f'钉钉消息发送异常: {e}')
        else:
            log.success('钉钉消息发送成功')
