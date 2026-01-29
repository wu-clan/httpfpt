from httpfpt.enums import StrEnum


class SeverityType(StrEnum):
    blocker = 'blocker'
    critical = 'critical'
    normal = 'normal'
    minor = 'minor'
    trivial = 'trivial'
