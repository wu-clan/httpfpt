from httpfpt.enums import StrEnum


class TeardownType(StrEnum):
    SQL = 'sql'
    HOOK = 'hook'
    EXTRACT = 'extract'
    ASSERT = 'assert'
    WAIT_TIME = 'wait_time'
