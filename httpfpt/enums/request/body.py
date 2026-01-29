from httpfpt.enums import StrEnum


class BodyType(StrEnum):
    form_data = 'form'
    x_www_form_urlencoded = 'x_form'
    binary = 'binary'
    GraphQL = 'GraphQL'
    TEXT = 'text'
    JavaScript = 'js'
    JSON = 'json'
    HTML = 'html'
    XML = 'xml'
