#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import allure

from fastpt.schema.allure.allure_attach import AllureAttachmentType
from fastpt.utils.file_control import get_file_property


def allure_step(title: str):
    """
    allure 操作步骤

    :return:
    """
    with allure.step(title):
        ...


def allure_attach(body=None, name=None, attachment_type: str = 'JSON', extension=None):
    """
    allure 报告上传附件

    :param body: 显示的内容
    :param name: 附件名称
    :param attachment_type: 文件类型，默认 JSON
    :param extension:
    :return:
    """
    allure.attach(
        body=body,
        name=name,
        attachment_type=getattr(AllureAttachmentType, attachment_type.upper(), None),
        extension=extension
    )


def allure_attach_file(filepath: dict, name=None, extension=None):
    """
    allure 报告上传附件

    :param filepath: 文件路径
    :param name:
    :param extension:
    :return:
    """
    for k, v in filepath.items():
        file_pp = get_file_property(v)
        filename = file_pp[0]
        filetype = file_pp[2]
        allure.attach.file(
            source=v,
            name=filename if name is None else name,
            attachment_type=getattr(AllureAttachmentType, filetype.upper(), None),
            extension=extension
        )
