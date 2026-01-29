from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from enum import Enum


def get_enum_values(enum_class: type[Enum]) -> list:
    return list(map(lambda ec: ec.value, enum_class))
