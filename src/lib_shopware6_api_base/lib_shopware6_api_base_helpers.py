# STDLIB
import pprint
from typing import Any

# EXT
from pydantic import BaseModel


def _filter_empty(data: Any) -> Any:
    """Recursively filter out None, empty lists, and empty dicts from nested structures."""
    if isinstance(data, dict):
        return {k: _filter_empty(v) for k, v in data.items() if v not in (None, [], {})}
    if isinstance(data, list):
        return [_filter_empty(item) for item in data]
    return data


def pprint_attrs(model_instance: BaseModel) -> None:
    """Pretty print a Pydantic model, excluding None, empty lists, and empty dicts (recursively)."""
    data = model_instance.model_dump(mode="python")
    filtered = _filter_empty(data)
    pprint.PrettyPrinter(sort_dicts=False).pprint(filtered)


def _is_not_empty(attribute: Any, value: Any) -> bool:
    """Filter out empty Lists and Dictionaries - kept for backward compatibility."""
    return value not in ({}, [])
