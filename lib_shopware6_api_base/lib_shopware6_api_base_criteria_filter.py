# STDLIB
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

# EXT

import attrs
from attrs import validators


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
        value: str  # todo check ! type is str, really ? on examples it seems it can be also int

    >>> # Setup
    >>> import pprint
    >>> pp = pprint.PrettyPrinter().pprint

    >>> # Test
    >>> my_filter = EqualsFilter('stock', 10)
    >>> pp(attrs.asdict(my_filter))
    {'field': 'stock', 'type': 'equals', 'value': 10}
    """

    # EqualsFilter}}}

    field: str = attrs.field(validator=attrs.validators.instance_of(str))
    value: str
    type: str = attrs.field(init=False, default="equals")


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
    >>> import pprint
    >>> pp = pprint.PrettyPrinter().pprint

    >>> # Test
    >>> my_filter = EqualsAnyFilter(field = 'productNumber', value = ["3fed029475fa4d4585f3a119886e0eb1", "77d26d011d914c3aa2c197c81241a45b"])
    >>> pp(attrs.asdict(my_filter))
    {'field': 'productNumber',
     'type': 'equals',
     'value': ['3fed029475fa4d4585f3a119886e0eb1',
               '77d26d011d914c3aa2c197c81241a45b']}

    """

    # EqualsAnyFilter}}}

    type: str = attrs.field(init=False, default="equals")
    field: str = attrs.field(init=True)
    value: List[str] = attrs.field(init=True)


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
    >>> import pprint
    >>> pp = pprint.PrettyPrinter().pprint

    >>> # Test
    >>> my_filter = ContainsFilter(field = 'productNumber', value = 'Lightweight')
    >>> pp(attrs.asdict(my_filter))
    {'field': 'productNumber', 'type': 'contains', 'value': 'Lightweight'}


    """

    # ContainsFilter}}}
    type: str = attrs.field(init=False, default="contains")
    field: str = attrs.field(init=True)
    value: List[str] = attrs.field(init=True)


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
    >>> import pprint
    >>> pp = pprint.PrettyPrinter().pprint

    >>> # Test (pass range type as string)
    >>> my_filter = RangeFilter(field = 'stock', parameters = {'gte': 20, 'lte': 30})
    >>> pp(attrs.asdict(my_filter))
    {'field': 'stock', 'parameters': {'gte': 20, 'lte': 30}, 'type': 'range'}

    >>> # Test (pass range type from 'range_filter' object)
    >>> my_filter = RangeFilter(field = 'stock', parameters = {range_filter.gte: 20, range_filter.lte: 30})
    >>> pp(attrs.asdict(my_filter))
    {'field': 'stock', 'parameters': {'gte': 20, 'lte': 30}, 'type': 'range'}

    >>> # Test (wrong range)
    >>> my_filter = RangeFilter(field = 'stock', parameters = {'gte': 20, 'less': 30})
    Traceback (most recent call last):
        ...
    ValueError: "less" is not a valid range

    """

    # RangeFilter}}}
    type: str = attrs.field(init=False, default="range")
    field: str = attrs.field()
    parameters: Dict[str, Union[int, datetime]] = attrs.field(validator=validators.instance_of(dict))

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
    >>> import pprint
    >>> pp = pprint.PrettyPrinter().pprint

    >>> # Test (pass operator as string)
    >>> my_filter = NotFilter('or', [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
    >>> pp(attrs.asdict(my_filter))
    {'operator': 'or',
     'queries': [{'field': 'stock', 'type': 'equals', 'value': 1},
                 {'field': 'availableStock', 'type': 'equals', 'value': 10}],
     'type': 'not'}


    >>> # Test (pass operator from 'not_filter_operator' object)
    >>> my_filter = NotFilter(not_filter_operator.or_, [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
    >>> pp(attrs.asdict(my_filter))
    {'operator': 'or',
     'queries': [{'field': 'stock', 'type': 'equals', 'value': 1},
                 {'field': 'availableStock', 'type': 'equals', 'value': 10}],
     'type': 'not'}

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
    >>> import pprint
    >>> pp = pprint.PrettyPrinter().pprint

    >>> # Test (pass operator as string)
    >>> my_filter = MultiFilter('or', [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
    >>> pp(attrs.asdict(my_filter))
    {'operator': 'or',
     'queries': [{'field': 'stock', 'type': 'equals', 'value': 1},
                 {'field': 'availableStock', 'type': 'equals', 'value': 10}],
     'type': 'multi'}


    >>> # Test (pass operator from 'not_filter_operator' object)
    >>> my_filter = MultiFilter(multi_filter_operator.or_, [EqualsFilter('stock', 1), EqualsFilter('availableStock', 10)])
    >>> pp(attrs.asdict(my_filter))
    {'operator': 'or',
     'queries': [{'field': 'stock', 'type': 'equals', 'value': 1},
                 {'field': 'availableStock', 'type': 'equals', 'value': 10}],
     'type': 'multi'}

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
    >>> import pprint
    >>> pp = pprint.PrettyPrinter().pprint

    >>> # Test
    >>> my_filter = PrefixFilter('name', 'Lightweight')
    >>> pp(attrs.asdict(my_filter))
    {'field': 'name', 'type': 'prefix', 'value': 'Lightweight'}

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
    >>> import pprint
    >>> pp = pprint.PrettyPrinter().pprint

    >>> # Test
    >>> my_filter = SuffixFilter('name', 'Lightweight')
    >>> pp(attrs.asdict(my_filter))
    {'field': 'name', 'type': 'suffix', 'value': 'Lightweight'}

    """

    # SuffixFilter}}}

    type: str = attrs.field(init=False, default="suffix")
    field: str = attrs.field(init=True)
    value: str = attrs.field(init=True)


FilterType = Union[EqualsFilter, EqualsAnyFilter, ContainsFilter, RangeFilter, NotFilter, MultiFilter, PrefixFilter, SuffixFilter]
