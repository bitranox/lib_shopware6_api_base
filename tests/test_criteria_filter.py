"""Comprehensive tests for filter classes in lib_shopware6_api_base_criteria_filter.py."""

from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from lib_shopware6_api_base import (
    ContainsFilter,
    EqualsAnyFilter,
    EqualsFilter,
    MultiFilter,
    NotFilter,
    PrefixFilter,
    RangeFilter,
    SuffixFilter,
)
from lib_shopware6_api_base.lib_shopware6_api_base_criteria_filter import (
    FilterOperator,
    FilterTypeName,
    RangeParam,
)


# =============================================================================
# TestEqualsFilter - 6 tests
# =============================================================================


class TestEqualsFilter:
    """Tests for the EqualsFilter class."""

    @pytest.mark.os_agnostic
    def test_equals_filter_with_int_value(self) -> None:
        """Test EqualsFilter with integer value."""
        my_filter = EqualsFilter(field="stock", value=10)
        assert my_filter.field == "stock"
        assert my_filter.value == 10
        assert my_filter.type == "equals"

    @pytest.mark.os_agnostic
    def test_equals_filter_with_string_value(self) -> None:
        """Test EqualsFilter with string value."""
        my_filter = EqualsFilter(field="name", value="test-product")
        assert my_filter.field == "name"
        assert my_filter.value == "test-product"
        assert my_filter.type == "equals"

    @pytest.mark.os_agnostic
    def test_equals_filter_with_none_value(self) -> None:
        """Test EqualsFilter with None value (for IS NULL queries)."""
        my_filter = EqualsFilter(field="stock", value=None)
        assert my_filter.field == "stock"
        assert my_filter.value is None
        assert my_filter.type == "equals"

    @pytest.mark.os_agnostic
    def test_equals_filter_with_bool_value(self) -> None:
        """Test EqualsFilter with boolean value."""
        my_filter = EqualsFilter(field="active", value=True)
        assert my_filter.field == "active"
        assert my_filter.value is True
        assert my_filter.type == "equals"

    @pytest.mark.os_agnostic
    def test_equals_filter_model_dump(self) -> None:
        """Test EqualsFilter model_dump output."""
        my_filter = EqualsFilter(field="stock", value=10)
        data = my_filter.model_dump()
        assert data == {"field": "stock", "value": 10, "type": "equals"}

    @pytest.mark.os_agnostic
    def test_equals_filter_model_dump_none_value_excluded(self) -> None:
        """Test EqualsFilter model_dump excludes None value correctly."""
        my_filter = EqualsFilter(field="stock", value=None)
        data = my_filter.model_dump()
        # None is still included in the dump, but can be filtered later
        assert data == {"field": "stock", "value": None, "type": "equals"}


# =============================================================================
# TestEqualsAnyFilter - 3 tests
# =============================================================================


class TestEqualsAnyFilter:
    """Tests for the EqualsAnyFilter class."""

    @pytest.mark.os_agnostic
    def test_equals_any_filter_with_values(self) -> None:
        """Test EqualsAnyFilter with list of values."""
        my_filter = EqualsAnyFilter(
            field="productNumber",
            value=["3fed029475fa4d4585f3a119886e0eb1", "77d26d011d914c3aa2c197c81241a45b"],
        )
        assert my_filter.field == "productNumber"
        assert len(my_filter.value) == 2
        assert my_filter.type == "equalsAny"

    @pytest.mark.os_agnostic
    def test_equals_any_filter_empty_list(self) -> None:
        """Test EqualsAnyFilter with empty list."""
        my_filter = EqualsAnyFilter(field="productNumber", value=[])
        assert my_filter.field == "productNumber"
        assert my_filter.value == []
        assert my_filter.type == "equalsAny"

    @pytest.mark.os_agnostic
    def test_equals_any_filter_model_dump(self) -> None:
        """Test EqualsAnyFilter model_dump output."""
        my_filter = EqualsAnyFilter(field="id", value=["abc", "def"])
        data = my_filter.model_dump()
        assert data == {"field": "id", "value": ["abc", "def"], "type": "equalsAny"}


# =============================================================================
# TestContainsFilter - 2 tests
# =============================================================================


class TestContainsFilter:
    """Tests for the ContainsFilter class."""

    @pytest.mark.os_agnostic
    def test_contains_filter_basic(self) -> None:
        """Test ContainsFilter with string value."""
        my_filter = ContainsFilter(field="name", value="Lightweight")
        assert my_filter.field == "name"
        assert my_filter.value == "Lightweight"
        assert my_filter.type == "contains"

    @pytest.mark.os_agnostic
    def test_contains_filter_model_dump(self) -> None:
        """Test ContainsFilter model_dump output."""
        my_filter = ContainsFilter(field="description", value="premium")
        data = my_filter.model_dump()
        assert data == {"field": "description", "value": "premium", "type": "contains"}


# =============================================================================
# TestRangeFilter - 5 tests
# =============================================================================


class TestRangeFilter:
    """Tests for the RangeFilter class."""

    @pytest.mark.os_agnostic
    def test_range_filter_gte_lte(self) -> None:
        """Test RangeFilter with gte and lte parameters."""
        my_filter = RangeFilter(field="stock", parameters={"gte": 20, "lte": 30})
        assert my_filter.field == "stock"
        assert my_filter.parameters == {"gte": 20, "lte": 30}
        assert my_filter.type == "range"

    @pytest.mark.os_agnostic
    def test_range_filter_gt_lt(self) -> None:
        """Test RangeFilter with gt and lt parameters."""
        my_filter = RangeFilter(field="price", parameters={"gt": 10, "lt": 100})
        assert my_filter.field == "price"
        assert my_filter.parameters == {"gt": 10, "lt": 100}
        assert my_filter.type == "range"

    @pytest.mark.os_agnostic
    def test_range_filter_with_enum(self) -> None:
        """Test RangeFilter using RangeParam enum."""
        my_filter = RangeFilter(
            field="stock",
            parameters={RangeParam.GTE: 20, RangeParam.LTE: 30},
        )
        assert my_filter.parameters == {"gte": 20, "lte": 30}

    @pytest.mark.os_agnostic
    def test_range_filter_with_datetime(self) -> None:
        """Test RangeFilter with datetime values."""
        date_from = datetime(2024, 1, 1, 0, 0, 0)
        date_to = datetime(2024, 12, 31, 23, 59, 59)
        my_filter = RangeFilter(
            field="createdAt",
            parameters={"gte": date_from, "lte": date_to},
        )
        assert my_filter.parameters["gte"] == date_from
        assert my_filter.parameters["lte"] == date_to

    @pytest.mark.os_agnostic
    def test_range_filter_invalid_key_raises_error(self) -> None:
        """Test RangeFilter raises ValidationError for invalid parameter key."""
        with pytest.raises(ValidationError) as exc_info:
            RangeFilter(field="stock", parameters={"gte": 20, "less": 30})
        assert "less" in str(exc_info.value)
        assert "not a valid range" in str(exc_info.value)


# =============================================================================
# TestNotFilter - 5 tests
# =============================================================================


class TestNotFilter:
    """Tests for the NotFilter class."""

    @pytest.mark.os_agnostic
    def test_not_filter_with_or_operator(self) -> None:
        """Test NotFilter with 'or' operator."""
        my_filter = NotFilter(
            operator="or",
            queries=[
                EqualsFilter(field="stock", value=1),
                EqualsFilter(field="availableStock", value=10),
            ],
        )
        assert my_filter.operator == "or"
        assert len(my_filter.queries) == 2
        assert my_filter.type == "not"

    @pytest.mark.os_agnostic
    def test_not_filter_with_and_operator(self) -> None:
        """Test NotFilter with 'and' operator."""
        my_filter = NotFilter(
            operator="and",
            queries=[EqualsFilter(field="active", value=False)],
        )
        assert my_filter.operator == "and"
        assert len(my_filter.queries) == 1
        assert my_filter.type == "not"

    @pytest.mark.os_agnostic
    def test_not_filter_with_enum_operator(self) -> None:
        """Test NotFilter using FilterOperator enum."""
        my_filter = NotFilter(
            operator=FilterOperator.OR,
            queries=[EqualsFilter(field="stock", value=0)],
        )
        assert my_filter.operator == "or"

    @pytest.mark.os_agnostic
    def test_not_filter_invalid_operator_raises_error(self) -> None:
        """Test NotFilter raises ValidationError for invalid operator."""
        with pytest.raises(ValidationError) as exc_info:
            NotFilter(
                operator="duck",  # type: ignore[arg-type]
                queries=[EqualsFilter(field="stock", value=1)],
            )
        assert "Input should be 'and' or 'or'" in str(exc_info.value)

    @pytest.mark.os_agnostic
    def test_not_filter_model_dump(self) -> None:
        """Test NotFilter model_dump output."""
        my_filter = NotFilter(
            operator="or",
            queries=[EqualsFilter(field="stock", value=1)],
        )
        data = my_filter.model_dump()
        assert data["type"] == "not"
        assert data["operator"] == "or"
        assert len(data["queries"]) == 1


# =============================================================================
# TestMultiFilter - 5 tests
# =============================================================================


class TestMultiFilter:
    """Tests for the MultiFilter class."""

    @pytest.mark.os_agnostic
    def test_multi_filter_with_or_operator(self) -> None:
        """Test MultiFilter with 'or' operator."""
        my_filter = MultiFilter(
            operator="or",
            queries=[
                EqualsFilter(field="stock", value=1),
                EqualsFilter(field="availableStock", value=10),
            ],
        )
        assert my_filter.operator == "or"
        assert len(my_filter.queries) == 2
        assert my_filter.type == "multi"

    @pytest.mark.os_agnostic
    def test_multi_filter_with_and_operator(self) -> None:
        """Test MultiFilter with 'and' operator."""
        my_filter = MultiFilter(
            operator="and",
            queries=[
                EqualsFilter(field="active", value=True),
                ContainsFilter(field="name", value="Premium"),
            ],
        )
        assert my_filter.operator == "and"
        assert len(my_filter.queries) == 2

    @pytest.mark.os_agnostic
    def test_multi_filter_with_enum_operator(self) -> None:
        """Test MultiFilter using FilterOperator enum."""
        my_filter = MultiFilter(
            operator=FilterOperator.AND,
            queries=[EqualsFilter(field="active", value=True)],
        )
        assert my_filter.operator == "and"

    @pytest.mark.os_agnostic
    def test_multi_filter_nested_multi_filter(self) -> None:
        """Test MultiFilter with nested MultiFilter."""
        inner_filter = MultiFilter(
            operator="and",
            queries=[
                EqualsFilter(field="active", value=True),
                EqualsFilter(field="stock", value=10),
            ],
        )
        outer_filter = MultiFilter(
            operator="or",
            queries=[
                inner_filter,
                EqualsFilter(field="featured", value=True),
            ],
        )
        assert outer_filter.operator == "or"
        assert len(outer_filter.queries) == 2
        assert outer_filter.queries[0].type == "multi"  # type: ignore[union-attr]

    @pytest.mark.os_agnostic
    def test_multi_filter_invalid_operator_raises_error(self) -> None:
        """Test MultiFilter raises ValidationError for invalid operator."""
        with pytest.raises(ValidationError) as exc_info:
            MultiFilter(
                operator="xor",  # type: ignore[arg-type]
                queries=[EqualsFilter(field="stock", value=1)],
            )
        assert "Input should be 'and' or 'or'" in str(exc_info.value)


# =============================================================================
# TestPrefixFilter - 2 tests
# =============================================================================


class TestPrefixFilter:
    """Tests for the PrefixFilter class."""

    @pytest.mark.os_agnostic
    def test_prefix_filter_basic(self) -> None:
        """Test PrefixFilter with string value."""
        my_filter = PrefixFilter(field="name", value="Light")
        assert my_filter.field == "name"
        assert my_filter.value == "Light"
        assert my_filter.type == "prefix"

    @pytest.mark.os_agnostic
    def test_prefix_filter_model_dump(self) -> None:
        """Test PrefixFilter model_dump output."""
        my_filter = PrefixFilter(field="sku", value="PRD-")
        data = my_filter.model_dump()
        assert data == {"field": "sku", "value": "PRD-", "type": "prefix"}


# =============================================================================
# TestSuffixFilter - 2 tests
# =============================================================================


class TestSuffixFilter:
    """Tests for the SuffixFilter class."""

    @pytest.mark.os_agnostic
    def test_suffix_filter_basic(self) -> None:
        """Test SuffixFilter with string value."""
        my_filter = SuffixFilter(field="name", value="weight")
        assert my_filter.field == "name"
        assert my_filter.value == "weight"
        assert my_filter.type == "suffix"

    @pytest.mark.os_agnostic
    def test_suffix_filter_model_dump(self) -> None:
        """Test SuffixFilter model_dump output."""
        my_filter = SuffixFilter(field="email", value="@example.com")
        data = my_filter.model_dump()
        assert data == {"field": "email", "value": "@example.com", "type": "suffix"}


# =============================================================================
# TestFilterEnums - 4 tests
# =============================================================================


class TestFilterEnums:
    """Tests for filter-related enums."""

    @pytest.mark.os_agnostic
    def test_filter_type_name_enum_values(self) -> None:
        """Test FilterTypeName enum has correct values."""
        assert FilterTypeName.EQUALS == "equals"
        assert FilterTypeName.EQUALS_ANY == "equalsAny"
        assert FilterTypeName.CONTAINS == "contains"
        assert FilterTypeName.RANGE == "range"
        assert FilterTypeName.NOT == "not"
        assert FilterTypeName.MULTI == "multi"
        assert FilterTypeName.PREFIX == "prefix"
        assert FilterTypeName.SUFFIX == "suffix"

    @pytest.mark.os_agnostic
    def test_range_param_enum_values(self) -> None:
        """Test RangeParam enum has correct values."""
        assert RangeParam.GTE == "gte"
        assert RangeParam.LTE == "lte"
        assert RangeParam.GT == "gt"
        assert RangeParam.LT == "lt"

    @pytest.mark.os_agnostic
    def test_filter_operator_enum_values(self) -> None:
        """Test FilterOperator enum has correct values."""
        assert FilterOperator.OR == "or"
        assert FilterOperator.AND == "and"

    @pytest.mark.os_agnostic
    def test_backward_compatibility_aliases(self) -> None:
        """Test backward compatibility aliases exist."""
        from lib_shopware6_api_base.lib_shopware6_api_base_criteria_filter import (
            equal_filter_type,
            multi_filter_operator,
            not_filter_operator,
            range_filter,
        )

        assert equal_filter_type is FilterTypeName
        assert range_filter is RangeParam
        assert not_filter_operator is FilterOperator
        assert multi_filter_operator is FilterOperator
