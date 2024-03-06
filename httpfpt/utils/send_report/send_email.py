#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import smtplib
import time

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Template

from httpfpt.common.log import log
from httpfpt.core.get_conf import httpfpt_config
from httpfpt.enums.email_type import EmailType
from httpfpt.utils.file_control import get_file_property


class SendMail:
    def __init__(self, content: dict, filename: str | None = None):
        self.content = content
        self.filename = filename

    def take_report(self) -> MIMEMultipart:
        """
        获取报告
        """
        msg = MIMEMultipart()
        msg['Subject'] = httpfpt_config.TEST_REPORT_TITLE
        msg['From'] = httpfpt_config.EMAIL_USER
        msg['date'] = time.strftime('%a, %d %b %Y %H:%M:%S %z')
        self.content.update({'test_title': httpfpt_config.TEST_REPORT_TITLE})
        self.content.update({'tester_name': httpfpt_config.TESTER_NAME})

        # 邮件正文
        with open('../../templates/email_notification.html', 'r', encoding='utf-8') as f:
            html = Template(f.read())

        mail_body = MIMEText(html.render(**self.content), _subtype='html', _charset='utf-8')
        msg.attach(mail_body)

        # 读取要发送的附件
        if self.filename:
            with open(self.filename, 'rb') as f:
                annex_body = f.read()
                # 邮件附件
                att1 = MIMEApplication(annex_body)
                att1['Content-Type'] = 'application/octet-stream'
                att1['Content-Disposition'] = f'attachment; filename={get_file_property(self.filename)[0]}'
                msg.attach(att1)

        return msg

    def take_error(self) -> MIMEMultipart:
        """
        获取错误信息
        """
        msg = MIMEMultipart()
        msg['Subject'] = 'HttpFpt 运行异常通知'
        msg['From'] = httpfpt_config.EMAIL_USER
        msg['date'] = time.strftime('%a, %d %b %Y %H:%M:%S %z')

        # 邮件正文
        with open('../../templates/email_notification.html', 'r', encoding='utf-8') as f:
            html = Template(f.read())

        mail_body = MIMEText(html.render(**self.content), _subtype='html', _charset='utf-8')
        msg.attach(mail_body)

        return msg

    def _send(self, msg_type: int) -> None:
        """
        发送邮件
        """
        msg = ''
        if msg_type == EmailType.REPORT:
            msg = self.take_report().as_string()
        elif msg_type == EmailType.ERROR:
            msg = self.take_error().as_string()
        if httpfpt_config.EMAIL_SSL:
            smtp = smtplib.SMTP_SSL(host=httpfpt_config.EMAIL_SERVER, port=httpfpt_config.EMAIL_PORT)
        else:
            smtp = smtplib.SMTP(host=httpfpt_config.EMAIL_SERVER, port=httpfpt_config.EMAIL_PORT)
        smtp.login(httpfpt_config.EMAIL_USER, httpfpt_config.EMAIL_PASSWORD)
        smtp.sendmail(httpfpt_config.EMAIL_USER, httpfpt_config.EMAIL_SEND_TO, msg)
        smtp.quit()

    def send_report(self) -> None:
        try:
            self._send(0)
        except Exception as e:
            log.error(f'测试报告邮件发送失败: {e}')
        else:
            log.info('测试报告邮件发送成功')

    def send_error(self) -> None:
        try:
            self._send(1)
        except Exception as e:
            log.error(f'运行异常通知邮件发送失败: {e}')
        else:
            log.info('运行异常通知邮件发送成功')
