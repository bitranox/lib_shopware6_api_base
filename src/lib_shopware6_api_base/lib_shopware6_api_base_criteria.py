# STDLIB
from typing import Any

# EXT
from pydantic import BaseModel, Field, model_validator

from .lib_shopware6_api_base_criteria_aggregation import *
from .lib_shopware6_api_base_criteria_filter import *
from .lib_shopware6_api_base_criteria_sorting import *

# proj
from .lib_shopware6_api_base_helpers import pprint_attrs

PostFilterType = "T"  # not implemented now


class Query(BaseModel):
    """
    see: https://shopware.stoplight.io/docs/store-api/ZG9jOjEwODExNzU2-search-queries#query
    Enables you to determine a ranking for the search result
    Use this parameter to create a weighted search query that returns a _score for each found entity.
    Any filter type can be used for the query. A score has to be defined for each query.
    The sum of the matching queries then results in the total _score value.

    parameter
        score   int
        query   FilterType

    >>> # Test
    >>> my_criteria = Criteria(
    ...    query=[Query(score=500, query=ContainsFilter(field='name', value='Bronze')),
    ...           Query(score=500, query=EqualsFilter(field='active', value='true')),
    ...           Query(score=100, query=EqualsFilter(field='manufacturerId', value='db3c17b1e572432eb4a4c881b6f9d68f'))])

    >>> pprint_attrs(my_criteria)
    {'query': [{'score': 500,
                'query': {'field': 'name', 'value': 'Bronze', 'type': 'contains'}},
               {'score': 500,
                'query': {'field': 'active', 'value': 'true', 'type': 'equals'}},
               {'score': 100,
                'query': {'field': 'manufacturerId',
                          'value': 'db3c17b1e572432eb4a4c881b6f9d68f',
                          'type': 'equals'}}]}

    """

    score: int
    query: FilterType


class Criteria(BaseModel):
    """
    see: https://shopware.stoplight.io/docs/store-api/ZG9jOjEwODExNzU2-search-queries

    structure of Criteria:

    parameter:

    aggregations  List[Aggregation]                    Specify aggregations to be computed on-the-fly
    associations  Dict['<name>', 'Criteria']           Allows to load additional data to the standard data of an entity
    filter        List[Filter]                         Allows you to filter the result and aggregations
    grouping      List['<fieldname>']                  allows you to group the result over fields
    ids           List['<id>']                         Limits the search to a list of Ids
    includes      Dict['apiAlias', List[<fieldname>]]  Restricts the output to the defined fields
    limit         Optional[int]                        Defines the number of entries to be determined
    page          Optional[int]                        Defines at which page the search result should start
    post-filter                           not implemented at the moment
    query         List[Query]                          Enables you to determine a ranking for the search result
    sort          List[Sort]                           Defines the sorting of the search result
    term          Optional[str]                        text search on all records based on their data model and weighting
                                                       Don't use term parameters together with query parameters.
    total-count-mode    Optional[int]                  Defines whether a total must be determined


    >>> # Test empty
    >>> my_criteria = Criteria()
    >>> pprint_attrs(my_criteria)
    {}

    >>> # Test Average aggregation
    >>> my_criteria = Criteria()
    >>> my_criteria.limit=1
    >>> my_criteria.includes['product'] = ['id', 'name']
    >>> my_criteria.aggregations = [AvgAggregation(name='average-price', field='price')]
    >>> pprint_attrs(my_criteria)
    {'limit': 1,
     'aggregations': [{'name': 'average-price', 'field': 'price', 'type': 'avg'}],
     'includes': {'product': ['id', 'name']}}

    >>> # Test Filter aggregation
    >>> my_criteria = Criteria(limit=1, includes={'product':['id', 'name']},
    ...     aggregations=[FilterAggregation(name='active-price-avg',
    ...                                    filter=[EqualsFilter(field='active', value=True)],
    ...                                    aggregation=AvgAggregation(name='avg-price',field='price'))])
    >>> pprint_attrs(my_criteria)
    {'limit': 1,
     'aggregations': [{'name': 'active-price-avg',
                       'filter': [{'field': 'active', 'value': True, 'type': 'equals'}],
                       'aggregation': {'name': 'avg-price',
                                       'field': 'price',
                                       'type': 'avg'},
                       'type': 'filter'}],
     'includes': {'product': ['id', 'name']}}

    >>> # Test Association
    >>> my_criteria = Criteria()
    >>> my_criteria.associations['products'] = Criteria(limit=5, filter=[EqualsFilter(field='active', value='true')])
    >>> pprint_attrs(my_criteria)
    {'associations': {'products': {'limit': 5,
                                   'filter': [{'field': 'active',
                                               'value': 'true',
                                               'type': 'equals'}]}}}

    >>> # Test append filters
    >>> my_criteria = Criteria()
    >>> my_criteria.page = 0
    >>> my_criteria.limit=1
    >>> my_criteria.filter.append(EqualsFilter(field='a', value='a'))
    >>> my_criteria.filter.append(EqualsFilter(field='b', value='b'))
    >>> my_criteria.filter.append(EqualsFilter(field='d', value='d'))
    >>> pprint_attrs(my_criteria)
    {'limit': 1,
     'page': 0,
     'filter': [{'field': 'a', 'value': 'a', 'type': 'equals'},
                {'field': 'b', 'value': 'b', 'type': 'equals'},
                {'field': 'd', 'value': 'd', 'type': 'equals'}]}

    >>> # Test set filters
    >>> my_criteria = Criteria()
    >>> my_criteria.filter = [EqualsFilter(field='a', value='a'), EqualsFilter(field='b', value='b'), EqualsFilter(field='d', value='d')]
    >>> pprint_attrs(my_criteria)
    {'filter': [{'field': 'a', 'value': 'a', 'type': 'equals'},
                {'field': 'b', 'value': 'b', 'type': 'equals'},
                {'field': 'd', 'value': 'd', 'type': 'equals'}]}

    >>> # Test Grouping
    >>> my_criteria = Criteria()
    >>> my_criteria.limit=5
    >>> my_criteria.grouping=['active']
    >>> pprint_attrs(my_criteria)
    {'limit': 5, 'grouping': ['active']}

    >>> # Test ids
    >>> # note that the limit is automatically set to 3, and page to 1, which is for our paginated request
    >>> my_criteria = Criteria()
    >>> my_criteria.ids=["012cd563cf8e4f0384eed93b5201cc98", "075fb241b769444bb72431f797fd5776", "090fcc2099794771935acf814e3fdb24"]
    >>> pprint_attrs(my_criteria)
    {'ids': ['012cd563cf8e4f0384eed93b5201cc98',
             '075fb241b769444bb72431f797fd5776',
             '090fcc2099794771935acf814e3fdb24']}

    >>> # Test ids with a limit already set, which should fail
    >>> # You can use either "limit" or "ids", but not both, see : https://github.com/bitranox/lib_shopware6_api_base#ids
    >>> my_criteria = Criteria(limit=5, ids=["012cd563cf8e4f0384eed93b5201cc98", "075fb241b769444bb72431f797fd5776", "090fcc2099794771935acf814e3fdb24"])
    Traceback (most recent call last):
        ...
    pydantic_core._pydantic_core.ValidationError: ...
    ...
    ...You can use either "limit" or "ids", but not both...
    ...

    >>> # Test includes
    >>> my_criteria = Criteria()
    >>> my_criteria.includes['product'] = ['id', 'name']
    >>> pprint_attrs(my_criteria)
    {'includes': {'product': ['id', 'name']}}

    >>> my_criteria = Criteria(page=1, limit=5)
    >>> pprint_attrs(my_criteria)
    {'limit': 5, 'page': 1}

    >>> # Test Query
    >>> my_criteria = Criteria(
    ...    query=[Query(score=500, query=ContainsFilter(field='name', value='Bronze')),
    ...           Query(score=500, query=EqualsFilter(field='active', value='true')),
    ...           Query(score=100, query=EqualsFilter(field='manufacturerId', value='db3c17b1e572432eb4a4c881b6f9d68f'))])
    >>> pprint_attrs(my_criteria)
    {'query': [{'score': 500,
                'query': {'field': 'name', 'value': 'Bronze', 'type': 'contains'}},
               {'score': 500,
                'query': {'field': 'active', 'value': 'true', 'type': 'equals'}},
               {'score': 100,
                'query': {'field': 'manufacturerId',
                          'value': 'db3c17b1e572432eb4a4c881b6f9d68f',
                          'type': 'equals'}}]}

    >>> # Test Sorting
    >>> my_criteria = Criteria(limit=5,
    ...                        sort=[FieldSorting(field='name', order='ASC', naturalSorting=True),
    ...                              DescFieldSorting(field='active')])
    >>> pprint_attrs(my_criteria)
    {'limit': 5,
     'sort': [{'field': 'name', 'order': 'ASC', 'naturalSorting': True},
              {'field': 'active', 'order': 'DESC'}]}

    """

    limit: int | None = None
    page: int | None = None
    aggregations: list[AggregationType] = Field(default_factory=list)
    associations: dict[str, "Criteria"] = Field(default_factory=dict)
    filter: list[FilterType] = Field(default_factory=list)
    grouping: list[str] = Field(default_factory=list)
    ids: list[str] = Field(default_factory=list)
    includes: dict[str, list[str]] = Field(default_factory=dict)
    post_filter: list[Any] = Field(default_factory=list)  # not implemented now
    query: list[Query] = Field(default_factory=list)
    sort: list[SortType] = Field(default_factory=list)
    term: str | None = None
    total_count_mode: int | None = None

    @model_validator(mode="after")
    def check_limit_ids_mutual_exclusivity(self) -> "Criteria":
        """Check that 'limit' and 'ids' are not both set."""
        if self.limit is not None and len(self.ids) > 0:
            raise ValueError(
                'You can use either "limit" or "ids", but not both, see : https://github.com/bitranox/lib_shopware6_api_base#ids'
            )
        return self

    def get_dict(self) -> dict[str, Any]:
        """Returns the data of the Pydantic model as a dictionary.
        None values, empty lists, and empty dictionaries will be filtered out.
        """
        data = self.model_dump(mode="python")
        return {k: v for k, v in data.items() if v not in (None, [], {})}


# Rebuild model for forward references
Criteria.model_rebuild()


def _is_not_empty(attribute: Any, value: Any) -> bool:
    """Filter out empty Lists and Dictionaries - kept for backward compatibility."""
    return value not in ({}, [])
