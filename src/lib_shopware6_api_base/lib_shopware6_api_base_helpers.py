# STDLIB
import pprint

# EXT
from pydantic import BaseModel


def pprint_model(model_instance: BaseModel) -> None:
    """Pretty-print a Pydantic model the way it is sent to Shopware.

    Uses ``model_dump(mode="json", exclude_defaults=True)``: JSON mode renders
    values exactly as they go over the wire (e.g. dates as ISO strings), while
    ``exclude_defaults`` is the idiomatic Pydantic way to drop unset/empty fields
    (``None``, ``[]``, ``{}`` are the field defaults here) yet keep discriminators
    such as a filter's ``type``.

    >>> from lib_shopware6_api_base import Criteria, EqualsFilter
    >>> pprint_model(Criteria())
    {}
    >>> pprint_model(EqualsFilter(field="active", value="true"))
    {'field': 'active', 'value': 'true', 'type': 'equals'}
    """
    pprint.PrettyPrinter(sort_dicts=False).pprint(model_instance.model_dump(mode="json", exclude_defaults=True, by_alias=True))
