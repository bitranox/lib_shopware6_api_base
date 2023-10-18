# STDLIB
import pprint
from typing import Any

# EXT
import attrs


def pprint_attrs(attrs_instance: Any) -> None:
    # pretty print attributes
    pprint.PrettyPrinter(sort_dicts=False).pprint(attrs.asdict(attrs_instance, filter=_is_not_empty))


def _is_not_empty(attribute: Any, value: Any) -> bool:  # noqa
    """Filter out empty Lists and Dictionaries for attrs attribute filters"""
    if value == dict():
        return False
    elif value == list():
        return False
    else:
        return True
