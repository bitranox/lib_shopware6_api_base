# STDLIB
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

# EXT
import attrs
from attrs import validators


# proj
try:
    from lib_shopware6_api_base_criteria_filter import *
except ImportError:  # pragma: no cover
    # Imports for Doctest
    from .lib_shopware6_api_base_criteria_filter import *  # type: ignore  # pragma: no cover


PostFilterType = "T"  # not implemented now
QueryType = "T"  # not implemented now
SortType = "T"  # not implemented now
AggregationType = "T"  # not implemented now
AssociationType = "T"  # not implemented now


# criteria{{{
@attrs.define()
class Criteria:
    """
    see: https://shopware.stoplight.io/docs/store-api/ZG9jOjEwODExNzU2-search-queries

    structure of Criteria:

    parameter:
    associations                not implemented at the moment
    includes                    not implemented at the moment
    ids                         not implemented at the moment
    total-count-mode            not implemented at the moment
    page    integer
    limit   integer
    filter  List[Filter]
    post-filter                 not implemented at the moment
    query                       not implemented at the moment
    term                        not implemented at the moment
    sort    List[Sort]
    aggregations                not implemented at the moment
    grouping                    not implemented at the moment

    >>> # Test shorthand set filters
    >>> my_criteria = Criteria()
    >>> my_criteria.filter = [EqualsFilter('a', 'a'), EqualsFilter('b', 'b'), EqualsFilter('d', 'd')]

    # criteria}}}

    >>> # Setup
    >>> import pprint
    >>> pp = pprint.PrettyPrinter().pprint

    >>> # Test append filters
    >>> my_criteria = Criteria()
    >>> my_criteria.page = 0
    >>> my_criteria.limit=1
    >>> my_criteria.filter.append(EqualsFilter('a', 'a'))
    >>> my_criteria.filter.append(EqualsFilter('b', 'b'))
    >>> my_criteria.filter.append(EqualsFilter('d', 'd'))
    >>> pp(my_criteria.get_dict())
    {'filter': [{'field': 'a', 'type': 'equals', 'value': 'a'},
                {'field': 'b', 'type': 'equals', 'value': 'b'},
                {'field': 'd', 'type': 'equals', 'value': 'd'}],
     'limit': 1,
     'page': 0}

    >>> # Test shorthand set filters
    >>> my_criteria = Criteria()
    >>> my_criteria.filter = [EqualsFilter('a', 'a'), EqualsFilter('b', 'b'), EqualsFilter('d', 'd')]
    >>> pp(my_criteria.get_dict())
    {'filter': [{'field': 'a', 'type': 'equals', 'value': 'a'},
                {'field': 'b', 'type': 'equals', 'value': 'b'},
                {'field': 'd', 'type': 'equals', 'value': 'd'}]}

    >>> # Test empty
    >>> my_criteria = Criteria()
    >>> pp(my_criteria.get_dict())
    {}

    """

    page: Optional[int] = None
    limit: Optional[int] = None
    filter: List[FilterType] = attrs.field(factory=list)
    sort: List["SortType"] = attrs.field(factory=list)  # type: ignore # not implemented now
    post_filter: List["PostFilterType"] = attrs.field(factory=list)  # type: ignore # not implemented now
    associations: Optional[AssociationType] = None  # type: ignore # not implemented now
    query: List["QueryType"] = attrs.field(factory=list)  # type: ignore # not implemented now
    term: Optional[str] = None  # not implemented now
    aggregations: List["AggregationType"] = attrs.field(factory=list)  # type: ignore # not implemented now
    grouping: Dict[str, Any] = dict()  # not implemented now

    def get_dict(self) -> Dict[str, Any]:
        result = attrs.asdict(self, filter=self._is_not_empty)
        return result

    @staticmethod
    def _is_not_empty(ignore: attrs.Attribute, value: Any) -> bool:  # type: ignore
        if value is None:
            return False
        elif value == dict():
            return False
        elif value == list():
            return False
        else:
            return True
