# STDLIB
from typing import Optional, Union

# EXT
import attrs

# proj
try:
    from lib_shopware6_api_base_helpers import get_pretty_printer
except ImportError:  # pragma: no cover
    # Imports for Doctest
    from .lib_shopware6_api_base_helpers import get_pretty_printer


# FieldSorting{{{
@attrs.define
class FieldSorting:
    """
    see: https://shopware.stoplight.io/docs/store-api/ZG9jOjEwODExNzU2-search-queries#sort
    The sort parameter allows to control the sorting of the result. Several sorts can be transferred at the same time.
    The field parameter defines which field is to be used for sorting.
    The order parameter defines the sort direction.
    The parameter naturalSorting allows to use a Natural Sorting Algorithm

    :parameter
        field : str
        order : str "ASC" or "DESC"
        naturalSorting : Optional[bool]

    >>> # Setup
    >>> pp = get_pretty_printer()

    >>> # Test
    >>> my_sorting = FieldSorting('name', 'ASC', True)
    >>> pp(attrs.asdict(my_sorting))
    {'field': 'name', 'order': 'ASC', 'naturalSorting': True}

    """

    # FieldSorting}}}
    field: str = attrs.field(validator=attrs.validators.instance_of(str))
    order: str = attrs.field(validator=attrs.validators.in_(["ASC", "DESC"]))
    naturalSorting: Optional[bool] = None


# AscFieldSorting{{{
@attrs.define
class AscFieldSorting:
    """
    see: https://shopware.stoplight.io/docs/store-api/ZG9jOjEwODExNzU2-search-queries#sort
    The sort parameter allows to control the sorting of the result. Several sorts can be transferred at the same time.
    The field parameter defines which field is to be used for sorting.
    The order parameter defines the sort direction.
    The parameter naturalSorting allows to use a Natural Sorting Algorithm

    :parameter
        field : str
        naturalSorting : Optional[bool]

    >>> # Setup
    >>> pp = get_pretty_printer()

    >>> # Test
    >>> my_sorting = AscFieldSorting('name', True)
    >>> pp(attrs.asdict(my_sorting))
    {'field': 'name', 'order': 'ASC', 'naturalSorting': True}

    """

    # AscFieldSorting}}}

    field: str = attrs.field(validator=attrs.validators.instance_of(str))
    order: str = attrs.field(init=False, default="ASC")
    naturalSorting: Optional[bool] = None


# DescFieldSorting{{{
@attrs.define
class DescFieldSorting:
    """
    see: https://shopware.stoplight.io/docs/store-api/ZG9jOjEwODExNzU2-search-queries#sort
    The sort parameter allows to control the sorting of the result. Several sorts can be transferred at the same time.
    The field parameter defines which field is to be used for sorting.
    The order parameter defines the sort direction.
    The parameter naturalSorting allows to use a Natural Sorting Algorithm

    :parameter
        field : str
        naturalSorting : Optional[bool]

    >>> # Setup
    >>> pp = get_pretty_printer()

    >>> # Test
    >>> my_sorting = DescFieldSorting('name', True)
    >>> pp(attrs.asdict(my_sorting))
    {'field': 'name', 'order': 'DESC', 'naturalSorting': True}

    """

    # DescFieldSorting}}}

    field: str = attrs.field(validator=attrs.validators.instance_of(str))
    order: str = attrs.field(init=False, default="DESC")
    naturalSorting: Optional[bool] = None


SortType = Union[FieldSorting, AscFieldSorting, DescFieldSorting]
