#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bs4 import BeautifulSoup

from fastpt.common.log import log
from fastpt.core import get_conf
from fastpt.core.path_conf import HTML_REPORT_PATH


class SendMail:

    def __init__(self, filename: str):
        self.filename = filename

    def take_messages(self):
        """
        生成邮件内容，和html报告附件
        """
        msg = MIMEMultipart()
        msg['Subject'] = get_conf.PROJECT_NAME + ' 自动化测试报告'
        msg['From'] = get_conf.EMAIL_USER
        msg['date'] = time.strftime('%a, %d %b %Y %H:%M:%S %z')

        # 读取要发送的附件
        with open(os.path.join(HTML_REPORT_PATH, self.filename), 'rb') as f:
            mail_body = str(f.read())

        # 邮件正文
        html = BeautifulSoup(mail_body, 'html.parser')
        result = []
        for _ in html.find_all('span'):
            result.append(_.text)
        context = '<h3>测试结果:</h3>' + '<br>'.join(result)
        msg.attach(MIMEText(context, _subtype='html', _charset='utf-8'))

        # 邮件附件
        att1 = MIMEText(mail_body, 'base64', 'utf-8')
        att1["Content-Type"] = 'application/octet-stream'
        att1["Content-Disposition"] = f'attachment; filename={self.filename}'
        msg.attach(att1)

        return msg

    def send(self):
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