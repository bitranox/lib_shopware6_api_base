# STDLIB
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

# EXT
import attrs
from attrs import validators

# proj
try:
    from lib_shopware6_api_base_helpers import get_pretty_printer
    from lib_shopware6_api_base_criteria_sorting import *
    from lib_shopware6_api_base_criteria_filter import *
except ImportError:  # pragma: no cover
    # Imports for Doctest
    from .lib_shopware6_api_base_helpers import get_pretty_printer
    from .lib_shopware6_api_base_criteria_sorting import *  # type: ignore  # pragma: no cover
    from .lib_shopware6_api_base_criteria_filter import *  # type: ignore  # pragma: no cover


@attrs.define
class _AggregationNames:
    """
    see: https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference
    definition of Aggregation Names

    """

    avg: str = "avg"
    count: str = "count"
    max: str = "max"
    min: str = "min"
    stats: str = "stats"
    sum: str = "sum"
    filter: str = "filter"
    terms: str = "terms"
    histogram: str = "histogram"


aggregation_names = _AggregationNames()


# AvgAggregation{{{
@attrs.define
class AvgAggregation:
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference
    The Avg aggregation makes it possible to calculate the average value for a field.
    The following SQL statement is executed in the background: AVG(price).

    :parameter:
        name: str
        field: str

    >>> # Setup
    >>> pp = get_pretty_printer()

    >>> # Test
    >>> my_aggregation = AvgAggregation('avg-price', 'price')
    >>> pp(attrs.asdict(my_aggregation))
    {'name': 'avg-price', 'type': 'avg', 'field': 'price'}

    """

    # AvgAggregation}}}

    name: str = attrs.field(validator=attrs.validators.instance_of(str))
    type: str = attrs.field(init=False, default="avg")
    field: str = attrs.field(validator=attrs.validators.instance_of(str))


# CountAggregation{{{
@attrs.define
class CountAggregation:
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference
    The count aggregation makes it possible to determine the number of entries for a field that are filled with a value.
    The following SQL statement is executed in the background: COUNT(DISTINCT(manufacturerId)).

    :parameter:
        name: str
        field: str

    >>> # Setup
    >>> pp = get_pretty_printer()

    >>> # Test
    >>> my_aggregation = CountAggregation('count-manufacturers', 'manufacturerId')
    >>> pp(attrs.asdict(my_aggregation))
    {'name': 'count-manufacturers', 'type': 'count', 'field': 'manufacturerId'}

    """

    # CountAggregation}}}

    name: str = attrs.field(validator=attrs.validators.instance_of(str))
    type: str = attrs.field(init=False, default="count")
    field: str = attrs.field(validator=attrs.validators.instance_of(str))


# MaxAggregation{{{
@attrs.define
class MaxAggregation:
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference
    The max aggregation allows you to determine the maximum value of a field.
    The following SQL statement is executed in the background: MAX(price).

    :parameter:
        name: str
        field: str

    >>> # Setup
    >>> pp = get_pretty_printer()

    >>> # Test
    >>> my_aggregation = MaxAggregation('max-price', 'price')
    >>> pp(attrs.asdict(my_aggregation))
    {'name': 'max-price', 'type': 'max', 'field': 'price'}

    """

    # MaxAggregation}}}

    name: str = attrs.field(validator=attrs.validators.instance_of(str))
    type: str = attrs.field(init=False, default="max")
    field: str = attrs.field(validator=attrs.validators.instance_of(str))


# MinAggregation{{{
@attrs.define
class MinAggregation:
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference
    The min aggregation makes it possible to determine the minimum value of a field.
    The following SQL statement is executed in the background: MIN(price)

    :parameter:
        name: str
        field: str

    >>> # Setup
    >>> pp = get_pretty_printer()

    >>> # Test
    >>> my_aggregation = MinAggregation('min-price', 'price')
    >>> pp(attrs.asdict(my_aggregation))
    {'name': 'min-price', 'type': 'min', 'field': 'price'}

    """

    # MinAggregation}}}

    name: str = attrs.field(validator=attrs.validators.instance_of(str))
    type: str = attrs.field(init=False, default="min")
    field: str = attrs.field(validator=attrs.validators.instance_of(str))


# SumAggregation{{{
@attrs.define
class SumAggregation:
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference
    The sum aggregation makes it possible to determine the total of a field.
    The following SQL statement is executed in the background: SUM(price)

    :parameter:
        name: str
        field: str

    >>> # Setup
    >>> pp = get_pretty_printer()

    >>> # Test
    >>> my_aggregation = SumAggregation('sum-price', 'price')
    >>> pp(attrs.asdict(my_aggregation))
    {'name': 'sum-price', 'type': 'sum', 'field': 'price'}

    """

    # SumAggregation}}}

    name: str = attrs.field(validator=attrs.validators.instance_of(str))
    type: str = attrs.field(init=False, default="sum")
    field: str = attrs.field(validator=attrs.validators.instance_of(str))


# StatsAggregation{{{
@attrs.define
class StatsAggregation:
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference
    The stats aggregation makes it possible to calculate several values at once for a field.
    This includes the previous max, min, avg and sum aggregation.
    The following SQL statement is executed in the background: SELECT MAX(price), MIN(price), AVG(price), SUM(price)

    :parameter:
        name: str
        field: str

    >>> # Setup
    >>> pp = get_pretty_printer()

    >>> # Test
    >>> my_aggregation = StatsAggregation('stats-price', 'price')
    >>> pp(attrs.asdict(my_aggregation))
    {'name': 'stats-price', 'type': 'stats', 'field': 'price'}

    """

    # StatsAggregation}}}

    name: str = attrs.field(validator=attrs.validators.instance_of(str))
    type: str = attrs.field(init=False, default="stats")
    field: str = attrs.field(validator=attrs.validators.instance_of(str))


# TermsAggregation{{{
@attrs.define
class TermsAggregation:
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference

    The terms aggregation belongs to the bucket aggregations.
    This allows you to determine the values of a field.
    The result contains each value once and how often this value occurs in the result.
    The terms aggregation also supports the following parameters:
        limit - Defines a maximum number of entries to be returned (default: zero)
        sort - Defines the order of the entries. By default the following is not sorted
        aggregation - Enables you to calculate further aggregations for each key
    The following SQL statement is executed in the background: SELECT DISTINCT(manufacturerId) as key, COUNT(manufacturerId) as count


    :parameter:
        name: str
        field: str
        sort: Optional[SortType]
        limit: Optional[int]
        aggregation: Optional[]

    >>> # Setup
    >>> pp = get_pretty_printer()

    >>> # Test
    >>> my_aggregation = TermsAggregation(name='manufacturer-ids', limit=3, sort=DescFieldSorting('manufacturer.name'), field='manufacturerId')
    >>> pp(attrs.asdict(my_aggregation))
    {'name': 'manufacturer-ids',
     'type': 'terms',
     'field': 'manufacturerId',
     'sort': {'field': 'manufacturer.name',
              'order': 'DESC',
              'naturalSorting': None},
     'limit': 3,
     'aggregation': None}

    """

    # TermsAggregation}}}

    name: str = attrs.field(validator=attrs.validators.instance_of(str))
    type: str = attrs.field(init=False, default="terms")
    field: str = attrs.field(validator=attrs.validators.instance_of(str))
    sort: Optional[SortType] = None
    limit: Optional[int] = attrs.field(validator=attrs.validators.instance_of(int), default=None)
    aggregation: Optional["AggregationType"] = None


# FilterAggregation{{{
@attrs.define
class FilterAggregation:
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference

    The filter aggregation belongs to the bucket aggregations.
    Unlike all other aggregations, this aggregation does not determine any result, it cannot be used alone.
    It is only used to further restrict the result of an aggregation in a criterion.
    Filters which defined inside the filter property of this aggregation type,
    are only used when calculating this aggregation.
    The filters have no effect on other aggregations or on the result of the search.

    :parameter:
        name: str
        sort: SortType
        filter: FilterType
        aggregation : AggregationType

    >>> # Setup
    >>> pp = get_pretty_printer()

    >>> # Test
    >>> my_aggregation = FilterAggregation(
    ...     name='active-price-avg',
    ...     filter=EqualsFilter(field='active', value=True),
    ...     aggregation=AvgAggregation(name='avg-price',field='price'))
    >>> pp(attrs.asdict(my_aggregation))
    {'name': 'active-price-avg',
     'type': 'filter',
     'filter': {'type': 'equals', 'field': 'active', 'value': True},
     'aggregation': {'name': 'avg-price', 'type': 'avg', 'field': 'price'}}

    """

    # FilterAggregation}}}

    name: str = attrs.field(validator=attrs.validators.instance_of(str))
    type: str = attrs.field(init=False, default="filter")
    filter: FilterType
    aggregation: "AggregationType"


# EntityAggregation{{{
@attrs.define
class EntityAggregation:
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference

    The entity aggregation is similar to the terms aggregation, it belongs to the bucket aggregations.
    As with terms aggregation, all unique values are determined for a field.
    The aggregation then uses the determined keys to load the defined entity. The keys are used here as ids.

    :parameter:
        name: str
        definition: str
        field: str

    >>> # Setup
    >>> pp = get_pretty_printer()

    >>> # Test
    >>> my_aggregation = EntityAggregation(name='manufacturers', definition='product_manufacturer', field='manufacturerId')
    >>> pp(attrs.asdict(my_aggregation))
    {'name': 'manufacturers',
     'type': 'entity',
     'definition': 'product_manufacturer',
     'field': 'manufacturerId'}
    """

    # EntityAggregation}}}

    name: str = attrs.field(validator=attrs.validators.instance_of(str))
    type: str = attrs.field(init=False, default="entity")
    definition: str = attrs.field(validator=attrs.validators.instance_of(str))
    field: str = attrs.field(validator=attrs.validators.instance_of(str))


# DateHistogramAggregation{{{
@attrs.define
class DateHistogramAggregation:
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference

    The histogram aggregation is used as soon as the data to be determined refers to a date field.
    With the histogram aggregation,
    one of the following date intervals can be given: minute, hour, day, week, month, quarter, year, day.
    This interval groups the result and calculates the corresponding count of hits.

    :parameter:
        name: str
        field: str
        interval: str ,  possible values: 'minute', 'hour', 'day', 'week', 'month', 'quarter', 'year', 'day'

    >>> # Setup
    >>> pp = get_pretty_printer()

    >>> # Test
    >>> my_aggregation = DateHistogramAggregation(name='release-dates', field='releaseDate', interval='month')
    >>> pp(attrs.asdict(my_aggregation))
    {'name': 'release-dates',
     'type': 'histogram',
     'field': 'releaseDate',
     'interval': 'month'}

    """

    # DateHistogramAggregation}}}

    name: str = attrs.field(validator=attrs.validators.instance_of(str))
    type: str = attrs.field(init=False, default="histogram")
    field: str = attrs.field(validator=attrs.validators.instance_of(str))
    interval: str = attrs.field(validator=attrs.validators.in_(["minute", "hour", "day", "week", "month", "quarter", "year", "day"]))


# NestingAggregations{{{
"""
see: https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference#nesting-aggregations
"""
# NestingAggregations}}}

AggregationType = Union[
    AvgAggregation,
    CountAggregation,
    MaxAggregation,
    MinAggregation,
    SumAggregation,
    StatsAggregation,
    TermsAggregation,
    FilterAggregation,
    EntityAggregation,
    DateHistogramAggregation,
]
