#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import smtplib
import time
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import NoReturn

from jinja2 import Template

from fastpt.common.log import log
from fastpt.core import get_conf
from fastpt.core.path_conf import HTML_EMAIL_REPORT_PATH
from fastpt.utils.file_control import get_file_property


class SendMail:

    def __init__(self, filename: str, content: dict):
        self.filename = filename
        self.content = content

    def take_messages(self):
        """
        生成邮件内容，和html报告附件
        """
        msg = MIMEMultipart()
        msg['Subject'] = get_conf.TEST_REPORT_TITLE
        msg['From'] = get_conf.EMAIL_USER
        msg['date'] = time.strftime('%a, %d %b %Y %H:%M:%S %z')
        self.content.update({'test_title': get_conf.PROJECT_NAME})
        self.content.update({'tester_name': get_conf.TESTER_NAME})

        # 邮件正文
        with open(os.path.join(HTML_EMAIL_REPORT_PATH, 'email_report.html'), 'r', encoding='utf-8') as f:
            html = Template(f.read())

        mail_body = MIMEText(html.render(**self.content), _subtype='html', _charset='utf-8')
        msg.attach(mail_body)

        # 读取要发送的附件
        with open(self.filename, 'rb') as f:
            annex_body = f.read()

        # 邮件附件
        att1 = MIMEApplication(annex_body)
        att1["Content-Type"] = 'application/octet-stream'
        att1["Content-Disposition"] = f'attachment; filename={get_file_property(self.filename)[0]}'
        msg.attach(att1)

        return msg

    def send(self) -> NoReturn:
        """
        发送邮件
        """
        try:
            if get_conf.EMAIL_SSL:
                smtp = smtplib.SMTP_SSL(host=get_conf.EMAIL_SERVER, port=get_conf.EMAIL_PORT)
            else:
                smtp = smtplib.SMTP(host=get_conf.EMAIL_SERVER, port=get_conf.EMAIL_PORT)
            smtp.login(get_conf.EMAIL_USER, get_conf.EMAIL_PASSWORD)
            smtp.sendmail(get_conf.EMAIL_USER, get_conf.EMAIL_SEND_TO, self.take_messages().as_string())
            smtp.quit()
        except Exception as e:
            log.error(f'测试报告邮件发送失败: {e}')
        else:
            log.success("测试报告邮件发送成功")
