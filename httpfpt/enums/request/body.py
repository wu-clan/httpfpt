#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from httpfpt.enums import StrEnum


class BodyType(StrEnum):
    form_data = 'form'
    x_www_form_urlencoded = 'x_form'
    # binary = 'binary'
    GraphQL = 'graphQL'
    TEXT = 'text'
    JavaScript = 'js'
    JSON = 'json'
    HTML = 'html'
    XML = 'xml'
