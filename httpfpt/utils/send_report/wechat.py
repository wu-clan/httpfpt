#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from httpfpt.common.log import log
from httpfpt.core.get_conf import config


class Wechat:
    def __init__(self, content: dict):
        self.content = content

    def send(self) -> None:
        # 发送企业微信消息
        try:
            import requests

            headers = {'Content-Type': 'application/json; charset=utf-8', 'Connection': 'close'}
            data = {
                'msgtype': 'markdown',
                'markdown': {
                    "content": "# {}\n"
                               "> 👤 测试人员:**{}**\n"
                               "> 🤖 测试结果:**{}**\n"
                               "> ✅ 通过用例:  <font color='info'>**{}**</font>\n"
                               "> 🔧 失败用例:  <font color='warning'>**{}**</font>\n"
                               "> ❌ 错误用例:  **{}**\n"
                               "> ⚠️ 跳过用例:  **{}**\n"
                               "> 🈴 总数用例:  **{}**\n"
                               "> ⌛ 开始时间:  **{}**\n"
                               "> ⏱️ 执行耗时:  **{}**\n"
                               "> ➡️ 查看报告: [点击跳转](https://foryourself)".format(
                        config.TEST_REPORT_TITLE,
                        config.TESTER_NAME,
                        self.content["result"],
                        self.content["passed"],
                        self.content['failed'],
                        self.content['error'],
                        self.content['skipped'],
                        self.content['total'],
                        self.content['started_time'],
                        self.content['elapsed'],
                    )
                },
            }
            response = requests.session().post(
                url=config.WECHAT_TALK_WEBHOOK,
                json=data,
                headers=headers,
                proxies=config.WECHAT_TALK_PROXY,  # type: ignore
            )
            response.raise_for_status()
        except Exception as e:
            log.error(f'企业微信消息发送异常: {e}')
        else:
            log.success('企业微信发送成功')
