#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum


class BodyType(Enum):
    none = None
    form_data = 'form'
    x_www_form_urlencoded = 'x_form'
    # binary = 'binary'
    GraphQL = 'graphQL'
    TEXT = 'text'
    JavaScript = 'js'
    JSON = 'json'
    HTML = 'html'
    XML = 'xml'
