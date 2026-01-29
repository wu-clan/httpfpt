from httpfpt.enums import StrEnum


class SetupType(StrEnum):
    TESTCASE = 'testcase'
    SQL = 'sql'
    HOOK = 'hook'
    WAIT_TIME = 'wait_time'
