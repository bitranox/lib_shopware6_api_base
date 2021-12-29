# STDLIB
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

# EXT
import attrs
from attrs import validators


# proj
try:
    from lib_shopware6_api_base_criteria_aggregation import *
    from lib_shopware6_api_base_criteria_filter import *
    from lib_shopware6_api_base_criteria_sorting import *
except ImportError:  # pragma: no cover
    # Imports for Doctest
    from .lib_shopware6_api_base_criteria_aggregation import *  # type: ignore  # pragma: no cover
    from .lib_shopware6_api_base_criteria_filter import *  # type: ignore  # pragma: no cover
    from .lib_shopware6_api_base_criteria_sorting import *  # type: ignore  # pragma: no cover


PostFilterType = "T"  # not implemented now


# Query{{{
@attrs.define
class Query:
    """
    see: https://shopware.stoplight.io/docs/store-api/ZG9jOjEwODExNzU2-search-queries#query
    Enables you to determine a ranking for the search result
    Use this parameter to create a weighted search query that returns a _score for each found entity.
    Any filter type can be used for the query. A score has to be defined for each query.
    The sum of the matching queries then results in the total _score value.

    :parameter
        score   int
        query   FilterType

    >>> # Setup
    >>> import pprint
    >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

    >>> # Test
    >>> my_criteria = Criteria(
    ...    query=[Query(score=500, query=ContainsFilter(field='name', value='Bronze')),
    ...           Query(score=500, query=EqualsFilter(field='active', value='true')),
    ...           Query(score=100, query=EqualsFilter(field='manufacturerId', value='db3c17b1e572432eb4a4c881b6f9d68f'))])
    >>> pp(my_criteria.get_dict())
    {'query': [{'score': 500,
                'query': {'type': 'contains', 'field': 'name', 'value': 'Bronze'}},
               {'score': 500,
                'query': {'type': 'equals', 'field': 'active', 'value': 'true'}},
               {'score': 100,
                'query': {'type': 'equals',
                          'field': 'manufacturerId',
                          'value': 'db3c17b1e572432eb4a4c881b6f9d68f'}}]}

    """

    # Query}}}
    score: int
    query: FilterType


# criteria{{{
@attrs.define
class Criteria:
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



    >>> # Setup
    >>> import pprint
    >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

    >>> # Test empty
    >>> my_criteria = Criteria()
    >>> pp(my_criteria.get_dict())
    {}

    >>> # Test Average aggregation
    >>> my_criteria = Criteria()
    >>> my_criteria.limit=1
    >>> my_criteria.includes['product'] = ['id', 'name']
    >>> my_criteria.aggregations = [AvgAggregation('average-price', 'price')]
    >>> pp(my_criteria.get_dict())
    {'limit': 1,
     'aggregations': [{'name': 'average-price', 'type': 'avg', 'field': 'price'}],
     'includes': {'product': ['id', 'name']}}

    >>> # Test Filter aggregation
    >>> my_criteria = Criteria(limit=1, includes={'product':['id', 'name']},
    ...     aggregations=FilterAggregation(name='active-price-avg',
    ...                                    filter=EqualsFilter(field='active', value=True),
    ...                                    aggregation=AvgAggregation(name='avg-price',field='price')))
    >>> pp(my_criteria.get_dict())
    {'limit': 1,
     'aggregations': {'name': 'active-price-avg',
                      'type': 'filter',
                      'filter': {'type': 'equals',
                                 'field': 'active',
                                 'value': True},
                      'aggregation': {'name': 'avg-price',
                                      'type': 'avg',
                                      'field': 'price'}},
     'includes': {'product': ['id', 'name']}}

    >>> # Association{{{
    >>> # Test Association
    >>> my_criteria = Criteria()
    >>> my_criteria.associations['products'] = Criteria(limit=5, filter=[EqualsFilter('active', 'true')])
    >>> pp(my_criteria.get_dict())
    {'associations': {'products': {'limit': 5,
                                   'filter': [{'type': 'equals',
                                               'field': 'active',
                                               'value': 'true'}]}}}
    >>> # Association}}}

    >>> # Test append filters
    >>> my_criteria = Criteria()
    >>> my_criteria.page = 0
    >>> my_criteria.limit=1
    >>> my_criteria.filter.append(EqualsFilter('a', 'a'))
    >>> my_criteria.filter.append(EqualsFilter('b', 'b'))
    >>> my_criteria.filter.append(EqualsFilter('d', 'd'))
    >>> pp(my_criteria.get_dict())
    {'limit': 1,
     'page': 0,
     'filter': [{'type': 'equals', 'field': 'a', 'value': 'a'},
                {'type': 'equals', 'field': 'b', 'value': 'b'},
                {'type': 'equals', 'field': 'd', 'value': 'd'}]}

    >>> # Test set filters
    >>> my_criteria = Criteria()
    >>> my_criteria.filter = [EqualsFilter('a', 'a'), EqualsFilter('b', 'b'), EqualsFilter('d', 'd')]
    >>> pp(my_criteria.get_dict())
    {'filter': [{'type': 'equals', 'field': 'a', 'value': 'a'},
                {'type': 'equals', 'field': 'b', 'value': 'b'},
                {'type': 'equals', 'field': 'd', 'value': 'd'}]}

    >>> # Grouping{{{
    >>> # Test Grouping
    >>> my_criteria = Criteria()
    >>> my_criteria.limit=5
    >>> my_criteria.grouping=['active']
    >>> pp(my_criteria.get_dict())
    {'limit': 5, 'grouping': ['active']}
    >>> # Grouping}}}

    >>> # ids{{{
    >>> # Test ids
    >>> my_criteria = Criteria()
    >>> my_criteria.ids=["012cd563cf8e4f0384eed93b5201cc98", "075fb241b769444bb72431f797fd5776", "090fcc2099794771935acf814e3fdb24"]
    >>> pp(my_criteria.get_dict())
    {'ids': ['012cd563cf8e4f0384eed93b5201cc98',
             '075fb241b769444bb72431f797fd5776',
             '090fcc2099794771935acf814e3fdb24']}

    >>> # ids}}}

    >>> # includes{{{
    >>> # Test includes
    >>> my_criteria = Criteria()
    >>> my_criteria.includes['product'] = ['id', 'name']
    >>> pp(my_criteria.get_dict())
    {'includes': {'product': ['id', 'name']}}

    >>> # includes}}}

    >>> # page&limit{{{
    >>> my_criteria = Criteria(page=1, limit=5)
    >>> pp(my_criteria.get_dict())
    {'limit': 5, 'page': 1}

    >>> # page&limit}}}

    >>> # Test Query
    >>> my_criteria = Criteria(
    ...    query=[Query(score=500, query=ContainsFilter(field='name', value='Bronze')),
    ...           Query(score=500, query=EqualsFilter(field='active', value='true')),
    ...           Query(score=100, query=EqualsFilter(field='manufacturerId', value='db3c17b1e572432eb4a4c881b6f9d68f'))])
    >>> pp(my_criteria.get_dict())
    {'query': [{'score': 500,
                'query': {'type': 'contains', 'field': 'name', 'value': 'Bronze'}},
               {'score': 500,
                'query': {'type': 'equals', 'field': 'active', 'value': 'true'}},
               {'score': 100,
                'query': {'type': 'equals',
                          'field': 'manufacturerId',
                          'value': 'db3c17b1e572432eb4a4c881b6f9d68f'}}]}

    >>> # Test Sorting
    >>> my_criteria = Criteria(limit=5,
    ...                        sort=[FieldSorting('name', 'ASC', True),
    ...                              DescFieldSorting('active')])
    >>> pp(my_criteria.get_dict())
    {'limit': 5,
     'sort': [{'field': 'name', 'order': 'ASC', 'naturalSorting': True},
              {'field': 'active', 'order': 'DESC'}]}

    """

    # criteria}}}

    limit: Optional[int] = None
    page: Optional[int] = None
    aggregations: List["AggregationType"] = attrs.field(factory=list)
    associations: Dict[str, "Criteria"] = attrs.field(factory=dict)
    filter: List[FilterType] = attrs.field(factory=list)
    grouping: List[str] = attrs.field(factory=list)
    ids: List[str] = attrs.field(factory=list)
    includes: Dict[str, List[str]] = attrs.field(factory=dict)
    post_filter: List["PostFilterType"] = attrs.field(factory=list)  # type: ignore # not implemented now
    query: List[Query] = attrs.field(factory=list)
    sort: List["SortType"] = attrs.field(factory=list)
    term: Optional[str] = None
    total_count_mode: Optional[int] = None

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


def get_dict(data: Any) -> Dict[str, Any]:
    """
    alternative to attrs.asdict

    :param data:
    :return:

    >>> # Setup
    >>> import pprint
    >>> pp = pprint.PrettyPrinter(sort_dicts=False).pprint

    >>> my_criteria = Criteria(limit=1, includes={'product':['id', 'name']},
    ...     aggregations=FilterAggregation(name='active-price-avg',
    ...                                    filter=EqualsFilter(field='active', value=True),
    ...                                    aggregation=AvgAggregation(name='avg-price',field='price')))
    >>> pp(get_dict(my_criteria))
    {'limit': 1,
     'aggregations': {'name': 'active-price-avg',
                      'type': 'filter',
                      'filter': {'type': 'equals',
                                 'field': 'active',
                                 'value': True},
                      'aggregation': {'name': 'avg-price',
                                      'type': 'avg',
                                      'field': 'price'}},
     'includes': {'product': ['id', 'name']}}

    """
    result_dict = dict()
    for slot in data.__slots__:
        if not slot.startswith("_"):
            value = getattr(data, slot)
            if hasattr(value, "__slots__"):
                result_dict[slot] = get_dict(value)
            elif _is_not_empty(value):
                result_dict[slot] = value
    return result_dict


def _is_not_empty(value: Any) -> bool:
    if value is None:
        return False
    elif value == dict():
        return False
    elif value == list():
        return False
    else:
        return True
