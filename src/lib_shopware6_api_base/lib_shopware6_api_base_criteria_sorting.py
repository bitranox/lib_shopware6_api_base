# STDLIB
from typing import Literal

# EXT
from pydantic import BaseModel, computed_field

__all__ = [
    "FieldSorting",
    "AscFieldSorting",
    "DescFieldSorting",
    "SortType",
]


class FieldSorting(BaseModel):
    """
    see: https://shopware.stoplight.io/docs/store-api/ZG9jOjEwODExNzU2-search-queries#sort
    The sort parameter allows to control the sorting of the result. Several sorts can be transferred at the same time.
    The field parameter defines which field is to be used for sorting.
    The order parameter defines the sort direction.
    The parameter naturalSorting allows to use a Natural Sorting Algorithm

    parameter:
        field : str
        order : str "ASC" or "DESC"
        naturalSorting : Optional[bool]

    >>> # Test
    >>> my_sorting = FieldSorting(field='name', order='ASC', naturalSorting=True)
    >>> pprint_attrs(my_sorting)
    {'field': 'name', 'order': 'ASC', 'naturalSorting': True}

    """

    field: str
    order: Literal["ASC", "DESC"]
    naturalSorting: bool | None = None


class AscFieldSorting(BaseModel):
    """
    see: https://shopware.stoplight.io/docs/store-api/ZG9jOjEwODExNzU2-search-queries#sort
    The sort parameter allows to control the sorting of the result. Several sorts can be transferred at the same time.
    The field parameter defines which field is to be used for sorting.
    The order parameter defines the sort direction.
    The parameter naturalSorting allows to use a Natural Sorting Algorithm

    parameter:
        field : str
        naturalSorting : Optional[bool]

    >>> # Test
    >>> my_sorting = AscFieldSorting(field='name', naturalSorting=True)
    >>> pprint_attrs(my_sorting)
    {'field': 'name', 'naturalSorting': True, 'order': 'ASC'}

    """

    field: str
    naturalSorting: bool | None = None

    @computed_field
    @property
    def order(self) -> str:
        return "ASC"


class DescFieldSorting(BaseModel):
    """
    see: https://shopware.stoplight.io/docs/store-api/ZG9jOjEwODExNzU2-search-queries#sort
    The sort parameter allows to control the sorting of the result. Several sorts can be transferred at the same time.
    The field parameter defines which field is to be used for sorting.
    The order parameter defines the sort direction.
    The parameter naturalSorting allows to use a Natural Sorting Algorithm

    parameter:
        field : str
        naturalSorting : Optional[bool]

    >>> # Test
    >>> my_sorting = DescFieldSorting(field='name', naturalSorting=True)
    >>> pprint_attrs(my_sorting)
    {'field': 'name', 'naturalSorting': True, 'order': 'DESC'}

    """

    field: str
    naturalSorting: bool | None = None

    @computed_field
    @property
    def order(self) -> str:
        return "DESC"


SortType = FieldSorting | AscFieldSorting | DescFieldSorting
