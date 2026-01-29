from httpfpt.enums import StrEnum


class AuthType(StrEnum):
    TOKEN = 'bearer_token'
    TOKEN_CUSTOM = 'bearer_token_custom'
    COOKIE = 'header_cookie'
