# STDLIB
"""Compatibility module for Python 3.10+ support.

This module provides compatibility shims for features added in Python 3.11+:
- StrEnum: Added in Python 3.11
- Self: Added to typing in Python 3.11
"""

import sys
from enum import Enum

__all__ = ["StrEnum", "Self"]

# StrEnum was added in Python 3.11
if sys.version_info >= (3, 11):
    from enum import StrEnum
else:

    class StrEnum(str, Enum):
        """String enum compatible with Python 3.10+.

        Behaves like enum.StrEnum from Python 3.11+.
        Members are also strings and can be used directly in string contexts.
        """

        def __new__(cls, value: str) -> "StrEnum":
            member = str.__new__(cls, value)
            member._value_ = value
            return member

        def __str__(self) -> str:
            return self.value

        @staticmethod
        def _generate_next_value_(name: str, start: int, count: int, last_values: list[str]) -> str:  # type: ignore[override]
            """Generate the next value when using auto()."""
            return name.lower()


# Self was added to typing in Python 3.11
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
