# STDLIB
import pprint
from typing import Any

# EXT
import attrs


def pprint_attrs(attrs_instance: Any):
    # pretty print attributes
    pprint.PrettyPrinter(sort_dicts=False).pprint(attrs.asdict(attrs_instance, filter=_is_not_empty))


def _is_not_empty(attribute: Any, value: Any) -> bool:
    """Filter out empty Lists and Dictionaries"""
    if value == dict():
        return False
    elif value == list():
        return False
    else:
        return True
