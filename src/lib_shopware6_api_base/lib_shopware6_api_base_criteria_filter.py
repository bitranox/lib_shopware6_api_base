# STDLIB
from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

# EXT
from pydantic import BaseModel, Field, computed_field, field_validator

# proj
from .lib_shopware6_api_base_helpers import pprint_attrs


class FilterTypeName(StrEnum):
    """Definition of Filter Types."""

    EQUALS = "equals"
    EQUALS_ANY = "equalsAny"
    CONTAINS = "contains"
    RANGE = "range"
    NOT = "not"
    MULTI = "multi"
    PREFIX = "prefix"
    SUFFIX = "suffix"


class RangeParam(StrEnum):
    """Definition of Range Filter Types."""

    GTE = "gte"
    LTE = "lte"
    GT = "gt"
    LT = "lt"


class FilterOperator(StrEnum):
    """Definition of Filter Operators for Not and Multi filters."""

    OR = "or"
    AND = "and"


# Backward compatibility aliases
equal_filter_type = FilterTypeName
range_filter = RangeParam
not_filter_operator = FilterOperator
multi_filter_operator = FilterOperator


class EqualsFilter(BaseModel):
    """
    see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
    The Equals filter allows you to check fields for an exact value.
    The following SQL statement is executed in the background: WHERE stock = 10.

    :parameter:
        field: str
        value: Union[str, int]      # probably also bool

    >>> # Test
    >>> my_filter = EqualsFilter(field='stock', value=10)
    >>> pprint_attrs(my_filter)
    {'field': 'stock', 'value': 10, 'type': 'equals'}

    >>> my_filter = EqualsFilter(field='stock', value=None)
    >>> pprint_attrs(my_filter)
    {'field': 'stock', 'type': 'equals'}

    """

    field: str
    value: None | str | int | bool

    @computed_field
    @property
    def type(self) -> str:
        return "equals"


class EqualsAnyFilter(BaseModel):
    """
    see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
    The EqualsAny filter allows you to filter a field where at least one of the defined values matches exactly.
    The following SQL statement is executed in the background:
    WHERE productNumber IN ('3fed029475fa4d4585f3a119886e0eb1', '77d26d011d914c3aa2c197c81241a45b').

    :parameter:
        field: str
        value: List[str]

    >>> # Test Keyword param
    >>> my_filter = EqualsAnyFilter(field = 'productNumber', value = ["3fed029475fa4d4585f3a119886e0eb1", "77d26d011d914c3aa2c197c81241a45b"])
    >>> pprint_attrs(my_filter)
    {'field': 'productNumber',
     'value': ['3fed029475fa4d4585f3a119886e0eb1',
               '77d26d011d914c3aa2c197c81241a45b'],
     'type': 'equalsAny'}

    >>> # Test positional param
    >>> my_filter = EqualsAnyFilter(field='productNumber', value=["3fed029475fa4d4585f3a119886e0eb1", "77d26d011d914c3aa2c197c81241a45b"])
    >>> pprint_attrs(my_filter)
    {'field': 'productNumber',
     'value': ['3fed029475fa4d4585f3a119886e0eb1',
               '77d26d011d914c3aa2c197c81241a45b'],
     'type': 'equalsAny'}

    """

    field: str
    value: list[str] = Field(default_factory=list)

    @computed_field
    @property
    def type(self) -> str:
        return "equalsAny"


class ContainsFilter(BaseModel):
    """
    see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
    The Contains Filter allows you to filter a field to an approximate value, where the passed value must be contained as a full value.
    The following SQL statement is executed in the background: WHERE name LIKE '%Lightweight%'.

    :parameter:
        field: str
        value: List[str]

    >>> # Test
    >>> my_filter = ContainsFilter(field = 'productNumber', value = 'Lightweight')
    >>> pprint_attrs(my_filter)
    {'field': 'productNumber', 'value': 'Lightweight', 'type': 'contains'}

    """

    field: str
    value: str

    @computed_field
    @property
    def type(self) -> str:
        return "contains"


class RangeFilter(BaseModel):
    """
    see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
    The Range filter allows you to filter a field to a value space. This can work with date or numerical values.
    Within the parameter property the following values are possible:
        gte => Greater than equals  (You might pass 'gte' or range_filter.GTE)
        lte => Less than equals     (You might pass 'lte' or range_filter.LTE)
        gt => Greater than          (You might pass 'gt' or range_filter.GT)
        lt => Less than             (You might pass 'lt' or range_filter.LT)

    :parameter:
        field: str
        parameters: Dict[str, Union[int, datetime]]

    >>> # Test (pass range type as string)
    >>> my_filter = RangeFilter(field = 'stock', parameters = {'gte': 20, 'lte': 30})
    >>> pprint_attrs(my_filter)
    {'field': 'stock', 'parameters': {'gte': 20, 'lte': 30}, 'type': 'range'}

    >>> # Test (pass range type from 'range_filter' object)
    >>> my_filter = RangeFilter(field = 'stock', parameters = {range_filter.GTE: 20, range_filter.LTE: 30})
    >>> pprint_attrs(my_filter)
    {'field': 'stock', 'parameters': {'gte': 20, 'lte': 30}, 'type': 'range'}

    >>> # Test (wrong range)
    >>> my_filter = RangeFilter(field = 'stock', parameters = {'gte': 20, 'less': 30})
    Traceback (most recent call last):
        ...
    pydantic_core._pydantic_core.ValidationError: ...
    ...
    ...Value error, "less" is not a valid range...
    ...

    """

    field: str
    parameters: dict[str, int | datetime] = Field(default_factory=dict)

    @computed_field
    @property
    def type(self) -> str:
        return "range"

    @field_validator("parameters")
    @classmethod
    def validate_range_keys(cls, v: dict[str, Any]) -> dict[str, Any]:
        valid_keys = {"gte", "lte", "gt", "lt"}
        for key in v:
            if key not in valid_keys:
                raise ValueError(f'"{key}" is not a valid range')
        return v


class NotFilter(BaseModel):
    """
    see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
    The Not Filter is a container which allows to negate any kind of filter.
    The operator allows you to define the combination of queries within the NOT filter ("OR" and "AND").
    The following SQL statement is executed in the background: WHERE !(stock = 1 OR availableStock = 1):

    :parameter:
        operator: 'or' | 'and'
        queries: List[Filter]

    >>> # Test (pass operator as string)
    >>> my_filter = NotFilter(operator='or', queries=[EqualsFilter(field='stock', value=1), EqualsFilter(field='availableStock', value=10)])
    >>> pprint_attrs(my_filter)
    {'operator': 'or',
     'queries': [{'field': 'stock', 'value': 1, 'type': 'equals'},
                 {'field': 'availableStock', 'value': 10, 'type': 'equals'}],
     'type': 'not'}

    >>> # Test (pass operator from 'not_filter_operator' object)
    >>> my_filter = NotFilter(operator=not_filter_operator.OR, queries=[EqualsFilter(field='stock', value=1), EqualsFilter(field='availableStock', value=10)])
    >>> pprint_attrs(my_filter)
    {'operator': 'or',
     'queries': [{'field': 'stock', 'value': 1, 'type': 'equals'},
                 {'field': 'availableStock', 'value': 10, 'type': 'equals'}],
     'type': 'not'}

    >>> # Test unknown operator
    >>> my_filter = NotFilter(operator='duck', queries=[EqualsFilter(field='stock', value=1), EqualsFilter(field='availableStock', value=10)])
    Traceback (most recent call last):
        ...
    pydantic_core._pydantic_core.ValidationError: ...
    ...
    ...Input should be 'and' or 'or'...
    ...

    """

    operator: Literal["and", "or"]
    queries: list["FilterType"] = Field(default_factory=list)

    @computed_field
    @property
    def type(self) -> str:
        return "not"


class MultiFilter(BaseModel):
    """
    see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
    The Multi Filter is a container, which allows to set logical links between filters.
    The operator allows you to define the links between the queries within the Multi filter ("OR" and "AND").
    The following SQL statement is executed in the background: WHERE (stock = 1 OR availableStock = 1)

    :parameter:
        operator: 'or' | 'and'
        queries: List[Filter]

    >>> # Test (pass operator as string)
    >>> my_filter = MultiFilter(operator='or', queries=[EqualsFilter(field='stock', value=1), EqualsFilter(field='availableStock', value=10)])
    >>> pprint_attrs(my_filter)
    {'operator': 'or',
     'queries': [{'field': 'stock', 'value': 1, 'type': 'equals'},
                 {'field': 'availableStock', 'value': 10, 'type': 'equals'}],
     'type': 'multi'}

    >>> # Test (pass operator from 'multi_filter_operator' object)
    >>> my_filter = MultiFilter(operator=multi_filter_operator.OR, queries=[EqualsFilter(field='stock', value=1), EqualsFilter(field='availableStock', value=10)])
    >>> pprint_attrs(my_filter)
    {'operator': 'or',
     'queries': [{'field': 'stock', 'value': 1, 'type': 'equals'},
                 {'field': 'availableStock', 'value': 10, 'type': 'equals'}],
     'type': 'multi'}

    >>> # Test unknown operator
    >>> my_filter = MultiFilter(operator='duck', queries=[EqualsFilter(field='stock', value=1), EqualsFilter(field='availableStock', value=10)])
    Traceback (most recent call last):
        ...
    pydantic_core._pydantic_core.ValidationError: ...
    ...
    ...Input should be 'and' or 'or'...
    ...

    """

    operator: Literal["and", "or"]
    queries: list["FilterType"] = Field(default_factory=list)

    @computed_field
    @property
    def type(self) -> str:
        return "multi"


class PrefixFilter(BaseModel):
    """
    see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
    The Prefix Filter allows you to filter a field to an approximate value, where the passed value must be the start of a full value.
    The following SQL statement is executed in the background: WHERE name LIKE 'Lightweight%'.

    :parameter:
        field: str
        value: str

    >>> # Test
    >>> my_filter = PrefixFilter(field='name', value='Lightweight')
    >>> pprint_attrs(my_filter)
    {'field': 'name', 'value': 'Lightweight', 'type': 'prefix'}

    """

    field: str
    value: str

    @computed_field
    @property
    def type(self) -> str:
        return "prefix"


class SuffixFilter(BaseModel):
    """
    see filter reference : https://developer.shopware.com/docs/resources/references/core-reference/dal-reference/filters-reference
    The Suffix Filter allows you to filter a field to an approximate value, where the passed value must be the end of a full value.
    The following SQL statement is executed in the background: WHERE name LIKE '%Lightweight'.

    :parameter:
        field: str
        value: str

    >>> # Test
    >>> my_filter = SuffixFilter(field='name', value='Lightweight')
    >>> pprint_attrs(my_filter)
    {'field': 'name', 'value': 'Lightweight', 'type': 'suffix'}

    """

    field: str
    value: str

    @computed_field
    @property
    def type(self) -> str:
        return "suffix"


FilterType = (
    EqualsFilter
    | EqualsAnyFilter
    | ContainsFilter
    | RangeFilter
    | NotFilter
    | MultiFilter
    | PrefixFilter
    | SuffixFilter
)

# Rebuild models with forward references
NotFilter.model_rebuild()
MultiFilter.model_rebuild()
