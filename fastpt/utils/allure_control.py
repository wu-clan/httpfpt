#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from typing import NoReturn, Union

import allure
from allure_commons.types import AttachmentType

from fastpt.utils.file_control import get_file_property


def allure_step(step: str, var: Union[str, dict]):
    """
    allure 操作步骤

    :param step: 操作步骤
    :param var: 操作步骤中的变量
    :return:
    """
    with allure.step(step):
        allure.attach(
            body=json.dumps(var, ensure_ascii=False, indent=2) if isinstance(var, dict) else var,
            name='JSON Serialize',
            attachment_type=AttachmentType.JSON,
        )


def allure_attach(body=None, name=None, attachment_type: str = 'JSON', extension=None) -> NoReturn:
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
        attachment_type=getattr(AttachmentType, attachment_type.upper(), None),
        extension=extension,
    )


def allure_attach_file(filepath: str, name=None, extension=None) -> NoReturn:
    """
    allure 报告上传附件

    :param filepath: 文件路径
    :param name:
    :param extension:
    :return:
    """
    file_property = get_file_property(filepath)
    filename = file_property[0]
    filetype = file_property[2]
    if filetype == 'txt':
        filetype = 'TEXT'
    elif filetype == 'uri':
        filetype = 'URI_LIST'
    allure.attach.file(
        source=filepath,
        name=name or filename,
        attachment_type=getattr(AttachmentType, filetype.upper(), None),
        extension=extension,
    )
