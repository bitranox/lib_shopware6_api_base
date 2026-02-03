# STDLIB
from enum import StrEnum
from typing import Literal

# EXT
from pydantic import BaseModel, Field, computed_field

from .lib_shopware6_api_base_criteria_filter import EqualsFilter, FilterType
from .lib_shopware6_api_base_criteria_sorting import DescFieldSorting, SortType

# proj
from .lib_shopware6_api_base_helpers import pprint_attrs


class AggregationTypeName(StrEnum):
    """
    see: https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference
    Definition of Aggregation Names.
    """

    AVG = "avg"
    COUNT = "count"
    MAX = "max"
    MIN = "min"
    STATS = "stats"
    SUM = "sum"
    FILTER = "filter"
    TERMS = "terms"
    HISTOGRAM = "histogram"


# Backward compatibility alias
aggregation_names = AggregationTypeName


class AvgAggregation(BaseModel):
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference
    The Avg aggregation makes it possible to calculate the average value for a field.
    The following SQL statement is executed in the background: AVG(price).

    :parameter:
        name: str
        field: str

    >>> # Test
    >>> my_aggregation = AvgAggregation(name='avg-price', field='price')
    >>> pprint_attrs(my_aggregation)
    {'name': 'avg-price', 'field': 'price', 'type': 'avg'}

    """

    name: str
    field: str

    @computed_field
    @property
    def type(self) -> str:
        return "avg"


class CountAggregation(BaseModel):
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference
    The count aggregation makes it possible to determine the number of entries for a field that are filled with a value.
    The following SQL statement is executed in the background: COUNT(DISTINCT(manufacturerId)).

    :parameter:
        name: str
        field: str

    >>> # Test
    >>> my_aggregation = CountAggregation(name='count-manufacturers', field='manufacturerId')
    >>> pprint_attrs(my_aggregation)
    {'name': 'count-manufacturers', 'field': 'manufacturerId', 'type': 'count'}

    """

    name: str
    field: str

    @computed_field
    @property
    def type(self) -> str:
        return "count"


class MaxAggregation(BaseModel):
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference
    The max aggregation allows you to determine the maximum value of a field.
    The following SQL statement is executed in the background: MAX(price).

    :parameter:
        name: str
        field: str

    >>> # Test
    >>> my_aggregation = MaxAggregation(name='max-price', field='price')
    >>> pprint_attrs(my_aggregation)
    {'name': 'max-price', 'field': 'price', 'type': 'max'}

    """

    name: str
    field: str

    @computed_field
    @property
    def type(self) -> str:
        return "max"


class MinAggregation(BaseModel):
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference
    The min aggregation makes it possible to determine the minimum value of a field.
    The following SQL statement is executed in the background: MIN(price)

    :parameter:
        name: str
        field: str

    >>> # Test
    >>> my_aggregation = MinAggregation(name='min-price', field='price')
    >>> pprint_attrs(my_aggregation)
    {'name': 'min-price', 'field': 'price', 'type': 'min'}

    """

    name: str
    field: str

    @computed_field
    @property
    def type(self) -> str:
        return "min"


class SumAggregation(BaseModel):
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference
    The sum aggregation makes it possible to determine the total of a field.
    The following SQL statement is executed in the background: SUM(price)

    :parameter:
        name: str
        field: str

    >>> # Test
    >>> my_aggregation = SumAggregation(name='sum-price', field='price')
    >>> pprint_attrs(my_aggregation)
    {'name': 'sum-price', 'field': 'price', 'type': 'sum'}

    """

    name: str
    field: str

    @computed_field
    @property
    def type(self) -> str:
        return "sum"


class StatsAggregation(BaseModel):
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference
    The stats aggregation makes it possible to calculate several values at once for a field.
    This includes the previous max, min, avg and sum aggregation.
    The following SQL statement is executed in the background: SELECT MAX(price), MIN(price), AVG(price), SUM(price)

    :parameter:
        name: str
        field: str

    >>> # Test
    >>> my_aggregation = StatsAggregation(name='stats-price', field='price')
    >>> pprint_attrs(my_aggregation)
    {'name': 'stats-price', 'field': 'price', 'type': 'stats'}

    """

    name: str
    field: str

    @computed_field
    @property
    def type(self) -> str:
        return "stats"


class TermsAggregation(BaseModel):
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

    >>> # Test
    >>> my_aggregation = TermsAggregation(name='manufacturer-ids', limit=3, sort=DescFieldSorting(field='manufacturer.name'), field='manufacturerId')
    >>> pprint_attrs(my_aggregation)
    {'name': 'manufacturer-ids',
     'field': 'manufacturerId',
     'sort': {'field': 'manufacturer.name', 'order': 'DESC'},
     'limit': 3,
     'type': 'terms'}

    """

    name: str
    field: str
    sort: SortType | None = None
    limit: int | None = None
    aggregation: "AggregationType | None" = None

    @computed_field
    @property
    def type(self) -> str:
        return "terms"


class FilterAggregation(BaseModel):
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference

    The filter aggregation belongs to the bucket aggregations.
    Unlike all other aggregations, this aggregation does not determine any result, it cannot be used alone.
    It is only used to further restrict the result of an aggregation in a criterion.
    Filters which defined inside the filter property of this aggregation type,
    are only used when calculating this aggregation.
    The filters have no effect on other aggregations or on the result of the search.

    parameter:
        name: str
        sort: SortType
        filter: List of FilterType
        aggregation : AggregationType

    >>> # Test
    >>> my_aggregation = FilterAggregation(
    ...     name='active-price-avg',
    ...     filter=[EqualsFilter(field='active', value=True)],
    ...     aggregation=AvgAggregation(name='avg-price',field='price'))
    >>> pprint_attrs(my_aggregation)
    {'name': 'active-price-avg',
     'filter': [{'field': 'active', 'value': True, 'type': 'equals'}],
     'aggregation': {'name': 'avg-price', 'field': 'price', 'type': 'avg'},
     'type': 'filter'}

    """

    name: str
    filter: list[FilterType] = Field(default_factory=list)
    aggregation: "AggregationType"

    @computed_field
    @property
    def type(self) -> str:
        return "filter"


class EntityAggregation(BaseModel):
    """
    see aggregations reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference

    The entity aggregation is similar to the terms aggregation, it belongs to the bucket aggregations.
    As with terms aggregation, all unique values are determined for a field.
    The aggregation then uses the determined keys to load the defined entity. The keys are used here as ids.

    :parameter:
        name: str
        definition: str
        field: str

    >>> # Test
    >>> my_aggregation = EntityAggregation(name='manufacturers', definition='product_manufacturer', field='manufacturerId')
    >>> pprint_attrs(my_aggregation)
    {'name': 'manufacturers',
     'definition': 'product_manufacturer',
     'field': 'manufacturerId',
     'type': 'entity'}
    """

    name: str
    definition: str
    field: str

    @computed_field
    @property
    def type(self) -> str:
        return "entity"


class DateHistogramAggregation(BaseModel):
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

    >>> # Test
    >>> my_aggregation = DateHistogramAggregation(name='release-dates', field='releaseDate', interval='month')
    >>> pprint_attrs(my_aggregation)
    {'name': 'release-dates', 'field': 'releaseDate', 'interval': 'month', 'type': 'histogram'}

    """

    name: str
    field: str
    interval: Literal["minute", "hour", "day", "week", "month", "quarter", "year"]

    @computed_field
    @property
    def type(self) -> str:
        return "histogram"


"""
see: https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/aggregations-reference#nesting-aggregations
"""

AggregationType = (
    AvgAggregation
    | CountAggregation
    | MaxAggregation
    | MinAggregation
    | SumAggregation
    | StatsAggregation
    | TermsAggregation
    | FilterAggregation
    | EntityAggregation
    | DateHistogramAggregation
)

# Rebuild models with forward references
TermsAggregation.model_rebuild()
FilterAggregation.model_rebuild()
