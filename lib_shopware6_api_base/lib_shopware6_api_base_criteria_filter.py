# STDLIB
from datetime import datetime
from typing import Any, Dict, List, Union

# EXT

import attrs
from attrs import validators

# proj
try:
    from lib_shopware6_api_base_helpers import get_pretty_printer
except ImportError:  # pragma: no cover
    # Imports for Doctest
    from .lib_shopware6_api_base_helpers import get_pretty_printer


@attrs.define
class _EqualFilterTypes:
    """
    definition of Filter Types

    """

    equals: str = "equals"
    equalsAny: str = "equalsAny"
    contains: str = "contains"
    range: str = "range"
    not_: str = "not"
    multi: str = "multi"
    prefix: str = "prefix"
    suffix: str = "suffix"


@attrs.define
class _RangeFilterTypes:
    """
    definition of Range Filter Types


    """

    gte: str = "gte"
    lte: str = "lte"
    gt: str = "gt"
    lt: str = "lt"


@attrs.define
class _NotFilterOperators:
    """
    definition of Not Filter Operators


    """

    or_: str = "or"
    and_: str = "and_"


@attrs.define
class _MultiFilterOperators:
    """
    definition of Multi Filter Operators


    """

    or_: str = "or"
    and_: str = "and_"


equal_filter_type = _EqualFilterTypes()
range_filter = _RangeFilterTypes()
not_filter_operator = _NotFilterOperators()
multi_filter_operator = _MultiFilterOperators()


# EqualsFilter{{{
@attrs.define
class EqualsFilter:
    """
    see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
    The Equals filter allows you to check fields for an exact value.
    The following SQL statement is executed in the background: WHERE stock = 10.

    :parameter:
        field: str
        value: Union[str, int]      # probably also bool

    >>> # Setup
    >>> pp = get_pretty_printer()

    >>> # Test
    >>> my_filter = EqualsFilter('stock', 10)
    >>> pp(attrs.asdict(my_filter))
    {'type': 'equals', 'field': 'stock', 'value': 10}

    >>> my_filter = EqualsFilter('stock', None)
    >>> pp(attrs.asdict(my_filter))
    {'type': 'equals', 'field': 'stock', 'value': None}

    """

    # EqualsFilter}}}

    type: str = attrs.field(init=False, default="equals")
    field: str = attrs.field(validator=attrs.validators.instance_of(str))
    value: Union[None, str, int]


# EqualsAnyFilter{{{
@attrs.define
class EqualsAnyFilter:
    """
    see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
    The EqualsAny filter allows you to filter a field where at least one of the defined values matches exactly.
    The following SQL statement is executed in the background:
    WHERE productNumber IN ('3fed029475fa4d4585f3a119886e0eb1', '77d26d011d914c3aa2c197c81241a45b').

    :parameter:
        field: str
        value: List[str]

    >>> # Setup
    >>> pp = get_pretty_printer()

    >>> # Test Keyword param
    >>> my_filter = EqualsAnyFilter(field = 'productNumber', value = ["3fed029475fa4d4585f3a119886e0eb1", "77d26d011d914c3aa2c197c81241a45b"])
    >>> pp(attrs.asdict(my_filter))
    {'type': 'equals',
     'field': 'productNumber',
     'value': ['3fed029475fa4d4585f3a119886e0eb1',
               '77d26d011d914c3aa2c197c81241a45b']}

    >>> # Test positional param
    >>> my_filter = EqualsAnyFilter('productNumber', ["3fed029475fa4d4585f3a119886e0eb1", "77d26d011d914c3aa2c197c81241a45b"])
    >>> pp(attrs.asdict(my_filter))
    {'type': 'equals',
     'field': 'productNumber',
     'value': ['3fed029475fa4d4585f3a119886e0eb1',
               '77d26d011d914c3aa2c197c81241a45b']}

    """

    # EqualsAnyFilter}}}

    type: str = attrs.field(init=False, default="equals")
    field: str = attrs.field(init=True, validator=attrs.validators.instance_of(str))
    value: List[str] = attrs.field(init=True, factory=list)


# ContainsFilter{{{
@attrs.define
class ContainsFilter:
    """
    see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
    The Contains Filter allows you to filter a field to an approximate value, where the passed value must be contained as a full value.
    The following SQL statement is executed in the background: WHERE name LIKE '%Lightweight%'.

    :parameter:
        field: str
        value: List[str]

    >>> # Setup
    >>> pp = get_pretty_printer()

    >>> # Test
    >>> my_filter = ContainsFilter(field = 'productNumber', value = 'Lightweight')
    >>> pp(attrs.asdict(my_filter))
    {'type': 'contains', 'field': 'productNumber', 'value': 'Lightweight'}


    """

    # ContainsFilter}}}
    type: str = attrs.field(init=False, default="contains")
    field: str = attrs.field(init=True, validator=attrs.validators.instance_of(str))
    value: List[str] = attrs.field(init=True, factory=list)


# RangeFilter{{{
@attrs.define
class RangeFilter:
    """
    see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
    The Range filter allows you to filter a field to a value space. This can work with date or numerical values.
    Within the parameter property the following values are possible:
        gte => Greater than equals  (You might pass 'gte' or range_filter.gte)
        lte => Less than equals     (You might pass 'lte' or range_filter.lte)
        gt => Greater than          (You might pass 'gt' or range_filter.gt)
        lt => Less than             (You might pass 'lt' or range_filter.lt)

    :parameter:
        field: str
        parameters: Dict[str, Union[int, datetime]]

    >>> # Setup
    >>> pp = get_pretty_printer()

    >>> # Test (pass range type as string)
    >>> my_filter = RangeFilter(field = 'stock', parameters = {'gte': 20, 'lte': 30})
    >>> pp(attrs.asdict(my_filter))
    {'type': 'range', 'field': 'stock', 'parameters': {'gte': 20, 'lte': 30}}

    >>> # Test (pass range type from 'range_filter' object)
    >>> my_filter = RangeFilter(field = 'stock', parameters = {range_filter.gte: 20, range_filter.lte: 30})
    >>> pp(attrs.asdict(my_filter))
    {'type': 'range', 'field': 'stock', 'parameters': {'gte': 20, 'lte': 30}}

    >>> # Test (wrong range)
    >>> my_filter = RangeFilter(field = 'stock', parameters = {'gte': 20, 'less': 30})
    Traceback (most recent call last):
        ...
    ValueError: "less" is not a valid range

    """

    # RangeFilter}}}
    type: str = attrs.field(init=False, default="range")
    field: str = attrs.field(validator=attrs.validators.instance_of(str))
    parameters: Dict[str, Union[int, datetime]] = attrs.field(validator=validators.instance_of(dict), factory=dict)

    @parameters.validator  # noqa
    def check(self, attribute: attrs.Attribute, parameters: Dict[str, Any]) -> None:  # type: ignore
        for parameter in parameters:
            if parameter not in ["gte", "lte", "gt", "lt"]:
                raise ValueError(f'"{parameter}" is not a valid range')


# NotFilter{{{
@attrs.define
class NotFilter:
    """
    see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
    The Not Filter is a container which allows to negate any kind of filter.
    The operator allows you to define the combination of queries within the NOT filter (OR and AND).
    The following SQL statement is executed in the background: WHERE !(stock = 1 OR availableStock = 1):

    :parameter:
        operator: 'or' | 'and'
        queries: List[Filter]

    >>> # Setup
    >>> pp = get_pretty_printer()

    >>> # Test (pass operator as string)
    >>> my_filter = NotFilter('or', [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
    >>> pp(attrs.asdict(my_filter))
    {'type': 'not',
     'operator': 'or',
     'queries': [{'type': 'equals', 'field': 'stock', 'value': 1},
                 {'type': 'equals', 'field': 'availableStock', 'value': 10}]}

    >>> # Test (pass operator from 'not_filter_operator' object)
    >>> my_filter = NotFilter(not_filter_operator.or_, [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
    >>> pp(attrs.asdict(my_filter))
    {'type': 'not',
     'operator': 'or',
     'queries': [{'type': 'equals', 'field': 'stock', 'value': 1},
                 {'type': 'equals', 'field': 'availableStock', 'value': 10}]}

    >>> # Test unknown operator
    >>> my_filter = NotFilter('duck', [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
    Traceback (most recent call last):
        ...
    ValueError: 'operator' must be in ['and', 'or'] (got 'duck')

    """

    # NotFilter}}}
    type: str = attrs.field(init=False, default="not")
    operator: str = attrs.field(init=True, validator=attrs.validators.in_(["and", "or"]))
    queries: List["FilterType"] = attrs.field(factory=list)


# MultiFilter{{{
@attrs.define
class MultiFilter:
    """
    see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
    The Multi Filter is a container, which allows to set logical links between filters.
    The operator allows you to define the links between the queries within the Multi filter (OR and AND).
    The following SQL statement is executed in the background: WHERE (stock = 1 OR availableStock = 1)

    :parameter:
        operator: 'or' | 'and'
        queries: List[Filter]

    >>> # Setup
    >>> pp = get_pretty_printer()

    >>> # Test (pass operator as string)
    >>> my_filter = MultiFilter('or', [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
    >>> pp(attrs.asdict(my_filter))
    {'type': 'multi',
     'operator': 'or',
     'queries': [{'type': 'equals', 'field': 'stock', 'value': 1},
                 {'type': 'equals', 'field': 'availableStock', 'value': 10}]}

    >>> # Test (pass operator from 'not_filter_operator' object)
    >>> my_filter = MultiFilter(multi_filter_operator.or_, [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
    >>> pp(attrs.asdict(my_filter))
    {'type': 'multi',
     'operator': 'or',
     'queries': [{'type': 'equals', 'field': 'stock', 'value': 1},
                 {'type': 'equals', 'field': 'availableStock', 'value': 10}]}

    >>> # Test unknown operator
    >>> my_filter = MultiFilter('duck', [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
    Traceback (most recent call last):
        ...
    ValueError: 'operator' must be in ['and', 'or'] (got 'duck')

    """

    # MultiFilter}}}

    type: str = attrs.field(init=False, default="multi")
    operator: str = attrs.field(init=True, validator=attrs.validators.in_(["and", "or"]))
    queries: List["FilterType"] = attrs.field(factory=list)


# PrefixFilter{{{
@attrs.define
class PrefixFilter:
    """
    see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
    The Prefix Filter allows you to filter a field to an approximate value, where the passed value must be the start of a full value.
    The following SQL statement is executed in the background: WHERE name LIKE 'Lightweight%'.

    :parameter:
        field: str
        value: str

    >>> # Setup
    >>> pp = get_pretty_printer()

    >>> # Test
    >>> my_filter = PrefixFilter('name', 'Lightweight')
    >>> pp(attrs.asdict(my_filter))
    {'type': 'prefix', 'field': 'name', 'value': 'Lightweight'}

    """

    # PrefixFilter}}}

    type: str = attrs.field(init=False, default="prefix")
    field: str = attrs.field(init=True)
    value: str = attrs.field(init=True)


# SuffixFilter{{{
@attrs.define
class SuffixFilter:
    """
    see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
    The Suffix Filter allows you to filter a field to an approximate value, where the passed value must be the end of a full value.
    The following SQL statement is executed in the background: WHERE name LIKE '%Lightweight'.

    :parameter:
        field: str
        value: str

    >>> # Setup
    >>> pp = get_pretty_printer()

    >>> # Test
    >>> my_filter = SuffixFilter('name', 'Lightweight')
    >>> pp(attrs.asdict(my_filter))
    {'type': 'suffix', 'field': 'name', 'value': 'Lightweight'}

    """

    # SuffixFilter}}}

    type: str = attrs.field(init=False, default="suffix")
    field: str = attrs.field(init=True)
    value: str = attrs.field(init=True)


FilterType = Union[EqualsFilter, EqualsAnyFilter, ContainsFilter, RangeFilter, NotFilter, MultiFilter, PrefixFilter, SuffixFilter]
