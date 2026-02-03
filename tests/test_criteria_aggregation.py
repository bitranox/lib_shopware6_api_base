"""Comprehensive tests for aggregation classes in lib_shopware6_api_base_criteria_aggregation.py."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from lib_shopware6_api_base import (
    AvgAggregation,
    CountAggregation,
    DateHistogramAggregation,
    DescFieldSorting,
    EntityAggregation,
    EqualsFilter,
    FilterAggregation,
    MaxAggregation,
    MinAggregation,
    StatsAggregation,
    SumAggregation,
    TermsAggregation,
)
from lib_shopware6_api_base.lib_shopware6_api_base_criteria_aggregation import (
    AggregationTypeName,
)

# =============================================================================
# TestAvgAggregation - 3 tests
# =============================================================================


class TestAvgAggregation:
    """Tests for the AvgAggregation class."""

    @pytest.mark.os_agnostic
    def test_avg_aggregation_basic(self) -> None:
        """Test AvgAggregation with name and field."""
        my_aggregation = AvgAggregation(name="avg-price", field="price")
        assert my_aggregation.name == "avg-price"
        assert my_aggregation.field == "price"
        assert my_aggregation.type == "avg"

    @pytest.mark.os_agnostic
    def test_avg_aggregation_model_dump(self) -> None:
        """Test AvgAggregation model_dump output."""
        my_aggregation = AvgAggregation(name="average-stock", field="stock")
        data = my_aggregation.model_dump()
        assert data == {"name": "average-stock", "field": "stock", "type": "avg"}

    @pytest.mark.os_agnostic
    def test_avg_aggregation_fixture(self, avg_aggregation: AvgAggregation) -> None:
        """Test using the avg_aggregation fixture."""
        assert avg_aggregation.name == "avg-price"
        assert avg_aggregation.field == "price"


# =============================================================================
# TestCountAggregation - 2 tests
# =============================================================================


class TestCountAggregation:
    """Tests for the CountAggregation class."""

    @pytest.mark.os_agnostic
    def test_count_aggregation_basic(self) -> None:
        """Test CountAggregation with name and field."""
        my_aggregation = CountAggregation(name="count-manufacturers", field="manufacturerId")
        assert my_aggregation.name == "count-manufacturers"
        assert my_aggregation.field == "manufacturerId"
        assert my_aggregation.type == "count"

    @pytest.mark.os_agnostic
    def test_count_aggregation_model_dump(self) -> None:
        """Test CountAggregation model_dump output."""
        my_aggregation = CountAggregation(name="product-count", field="id")
        data = my_aggregation.model_dump()
        assert data == {"name": "product-count", "field": "id", "type": "count"}


# =============================================================================
# TestMaxAggregation - 2 tests
# =============================================================================


class TestMaxAggregation:
    """Tests for the MaxAggregation class."""

    @pytest.mark.os_agnostic
    def test_max_aggregation_basic(self) -> None:
        """Test MaxAggregation with name and field."""
        my_aggregation = MaxAggregation(name="max-price", field="price")
        assert my_aggregation.name == "max-price"
        assert my_aggregation.field == "price"
        assert my_aggregation.type == "max"

    @pytest.mark.os_agnostic
    def test_max_aggregation_model_dump(self) -> None:
        """Test MaxAggregation model_dump output."""
        my_aggregation = MaxAggregation(name="highest-stock", field="stock")
        data = my_aggregation.model_dump()
        assert data == {"name": "highest-stock", "field": "stock", "type": "max"}


# =============================================================================
# TestMinAggregation - 2 tests
# =============================================================================


class TestMinAggregation:
    """Tests for the MinAggregation class."""

    @pytest.mark.os_agnostic
    def test_min_aggregation_basic(self) -> None:
        """Test MinAggregation with name and field."""
        my_aggregation = MinAggregation(name="min-price", field="price")
        assert my_aggregation.name == "min-price"
        assert my_aggregation.field == "price"
        assert my_aggregation.type == "min"

    @pytest.mark.os_agnostic
    def test_min_aggregation_model_dump(self) -> None:
        """Test MinAggregation model_dump output."""
        my_aggregation = MinAggregation(name="lowest-stock", field="stock")
        data = my_aggregation.model_dump()
        assert data == {"name": "lowest-stock", "field": "stock", "type": "min"}


# =============================================================================
# TestSumAggregation - 2 tests
# =============================================================================


class TestSumAggregation:
    """Tests for the SumAggregation class."""

    @pytest.mark.os_agnostic
    def test_sum_aggregation_basic(self) -> None:
        """Test SumAggregation with name and field."""
        my_aggregation = SumAggregation(name="sum-price", field="price")
        assert my_aggregation.name == "sum-price"
        assert my_aggregation.field == "price"
        assert my_aggregation.type == "sum"

    @pytest.mark.os_agnostic
    def test_sum_aggregation_model_dump(self) -> None:
        """Test SumAggregation model_dump output."""
        my_aggregation = SumAggregation(name="total-stock", field="stock")
        data = my_aggregation.model_dump()
        assert data == {"name": "total-stock", "field": "stock", "type": "sum"}


# =============================================================================
# TestStatsAggregation - 2 tests
# =============================================================================


class TestStatsAggregation:
    """Tests for the StatsAggregation class."""

    @pytest.mark.os_agnostic
    def test_stats_aggregation_basic(self) -> None:
        """Test StatsAggregation with name and field."""
        my_aggregation = StatsAggregation(name="stats-price", field="price")
        assert my_aggregation.name == "stats-price"
        assert my_aggregation.field == "price"
        assert my_aggregation.type == "stats"

    @pytest.mark.os_agnostic
    def test_stats_aggregation_model_dump(self) -> None:
        """Test StatsAggregation model_dump output."""
        my_aggregation = StatsAggregation(name="price-statistics", field="price")
        data = my_aggregation.model_dump()
        assert data == {"name": "price-statistics", "field": "price", "type": "stats"}


# =============================================================================
# TestTermsAggregation - 5 tests
# =============================================================================


class TestTermsAggregation:
    """Tests for the TermsAggregation class."""

    @pytest.mark.os_agnostic
    def test_terms_aggregation_basic(self) -> None:
        """Test TermsAggregation with name and field."""
        my_aggregation = TermsAggregation(name="manufacturer-ids", field="manufacturerId")
        assert my_aggregation.name == "manufacturer-ids"
        assert my_aggregation.field == "manufacturerId"
        assert my_aggregation.type == "terms"
        assert my_aggregation.limit is None
        assert my_aggregation.sort is None

    @pytest.mark.os_agnostic
    def test_terms_aggregation_with_limit(self) -> None:
        """Test TermsAggregation with limit."""
        my_aggregation = TermsAggregation(
            name="top-manufacturers",
            field="manufacturerId",
            limit=10,
        )
        assert my_aggregation.limit == 10

    @pytest.mark.os_agnostic
    def test_terms_aggregation_with_sort(self) -> None:
        """Test TermsAggregation with sort."""
        my_aggregation = TermsAggregation(
            name="manufacturer-ids",
            field="manufacturerId",
            limit=3,
            sort=DescFieldSorting(field="manufacturer.name"),
        )
        assert my_aggregation.sort is not None
        assert my_aggregation.sort.order == "DESC"  # type: ignore[union-attr]

    @pytest.mark.os_agnostic
    def test_terms_aggregation_with_nested_aggregation(self) -> None:
        """Test TermsAggregation with nested aggregation."""
        my_aggregation = TermsAggregation(
            name="manufacturer-with-avg-price",
            field="manufacturerId",
            aggregation=AvgAggregation(name="avg-price", field="price"),
        )
        assert my_aggregation.aggregation is not None
        assert my_aggregation.aggregation.type == "avg"

    @pytest.mark.os_agnostic
    def test_terms_aggregation_model_dump(self) -> None:
        """Test TermsAggregation model_dump output."""
        my_aggregation = TermsAggregation(
            name="manufacturer-ids",
            field="manufacturerId",
            limit=3,
            sort=DescFieldSorting(field="manufacturer.name"),
        )
        data = my_aggregation.model_dump()
        assert data["name"] == "manufacturer-ids"
        assert data["field"] == "manufacturerId"
        assert data["limit"] == 3
        assert data["sort"]["order"] == "DESC"
        assert data["type"] == "terms"


# =============================================================================
# TestFilterAggregation - 3 tests
# =============================================================================


class TestFilterAggregation:
    """Tests for the FilterAggregation class."""

    @pytest.mark.os_agnostic
    def test_filter_aggregation_basic(self) -> None:
        """Test FilterAggregation with filter and nested aggregation."""
        my_aggregation = FilterAggregation(
            name="active-price-avg",
            filter=[EqualsFilter(field="active", value=True)],
            aggregation=AvgAggregation(name="avg-price", field="price"),
        )
        assert my_aggregation.name == "active-price-avg"
        assert len(my_aggregation.filter) == 1
        assert my_aggregation.aggregation.type == "avg"
        assert my_aggregation.type == "filter"

    @pytest.mark.os_agnostic
    def test_filter_aggregation_multiple_filters(self) -> None:
        """Test FilterAggregation with multiple filters."""
        my_aggregation = FilterAggregation(
            name="filtered-count",
            filter=[
                EqualsFilter(field="active", value=True),
                EqualsFilter(field="stock", value=10),
            ],
            aggregation=CountAggregation(name="count", field="id"),
        )
        assert len(my_aggregation.filter) == 2

    @pytest.mark.os_agnostic
    def test_filter_aggregation_model_dump(self) -> None:
        """Test FilterAggregation model_dump output."""
        my_aggregation = FilterAggregation(
            name="active-price-avg",
            filter=[EqualsFilter(field="active", value=True)],
            aggregation=AvgAggregation(name="avg-price", field="price"),
        )
        data = my_aggregation.model_dump()
        assert data["name"] == "active-price-avg"
        assert data["type"] == "filter"
        assert len(data["filter"]) == 1
        assert data["filter"][0]["type"] == "equals"
        assert data["aggregation"]["type"] == "avg"


# =============================================================================
# TestEntityAggregation - 2 tests
# =============================================================================


class TestEntityAggregation:
    """Tests for the EntityAggregation class."""

    @pytest.mark.os_agnostic
    def test_entity_aggregation_basic(self) -> None:
        """Test EntityAggregation with name, definition, and field."""
        my_aggregation = EntityAggregation(
            name="manufacturers",
            definition="product_manufacturer",
            field="manufacturerId",
        )
        assert my_aggregation.name == "manufacturers"
        assert my_aggregation.definition == "product_manufacturer"
        assert my_aggregation.field == "manufacturerId"
        assert my_aggregation.type == "entity"

    @pytest.mark.os_agnostic
    def test_entity_aggregation_model_dump(self) -> None:
        """Test EntityAggregation model_dump output."""
        my_aggregation = EntityAggregation(
            name="categories",
            definition="category",
            field="categoryId",
        )
        data = my_aggregation.model_dump()
        assert data == {
            "name": "categories",
            "definition": "category",
            "field": "categoryId",
            "type": "entity",
        }


# =============================================================================
# TestDateHistogramAggregation - 4 tests
# =============================================================================


class TestDateHistogramAggregation:
    """Tests for the DateHistogramAggregation class."""

    @pytest.mark.os_agnostic
    def test_date_histogram_aggregation_month(self) -> None:
        """Test DateHistogramAggregation with month interval."""
        my_aggregation = DateHistogramAggregation(
            name="release-dates",
            field="releaseDate",
            interval="month",
        )
        assert my_aggregation.name == "release-dates"
        assert my_aggregation.field == "releaseDate"
        assert my_aggregation.interval == "month"
        assert my_aggregation.type == "histogram"

    @pytest.mark.os_agnostic
    def test_date_histogram_aggregation_all_intervals(self) -> None:
        """Test DateHistogramAggregation with all valid intervals."""
        intervals = ["minute", "hour", "day", "week", "month", "quarter", "year"]
        for interval in intervals:
            my_aggregation = DateHistogramAggregation(
                name=f"by-{interval}",
                field="createdAt",
                interval=interval,  # type: ignore[arg-type]
            )
            assert my_aggregation.interval == interval

    @pytest.mark.os_agnostic
    def test_date_histogram_aggregation_invalid_interval(self) -> None:
        """Test DateHistogramAggregation raises error for invalid interval."""
        with pytest.raises(ValidationError):
            DateHistogramAggregation(
                name="invalid",
                field="createdAt",
                interval="invalid",  # type: ignore[arg-type]
            )

    @pytest.mark.os_agnostic
    def test_date_histogram_aggregation_model_dump(self) -> None:
        """Test DateHistogramAggregation model_dump output."""
        my_aggregation = DateHistogramAggregation(
            name="orders-by-week",
            field="orderDate",
            interval="week",
        )
        data = my_aggregation.model_dump()
        assert data == {
            "name": "orders-by-week",
            "field": "orderDate",
            "interval": "week",
            "type": "histogram",
        }


# =============================================================================
# TestAggregationEnum - 3 tests
# =============================================================================


class TestAggregationEnum:
    """Tests for the AggregationTypeName enum."""

    @pytest.mark.os_agnostic
    def test_aggregation_type_name_values(self) -> None:
        """Test AggregationTypeName enum has correct values."""
        assert AggregationTypeName.AVG == "avg"
        assert AggregationTypeName.COUNT == "count"
        assert AggregationTypeName.MAX == "max"
        assert AggregationTypeName.MIN == "min"
        assert AggregationTypeName.STATS == "stats"
        assert AggregationTypeName.SUM == "sum"
        assert AggregationTypeName.FILTER == "filter"
        assert AggregationTypeName.TERMS == "terms"
        assert AggregationTypeName.HISTOGRAM == "histogram"

    @pytest.mark.os_agnostic
    def test_aggregation_type_name_count(self) -> None:
        """Test AggregationTypeName enum has correct number of values."""
        assert len(AggregationTypeName) == 9

    @pytest.mark.os_agnostic
    def test_backward_compatibility_alias(self) -> None:
        """Test backward compatibility alias exists."""
        from lib_shopware6_api_base.lib_shopware6_api_base_criteria_aggregation import (
            aggregation_names,
        )

        assert aggregation_names is AggregationTypeName


# =============================================================================
# Additional Integration Tests - 2 tests
# =============================================================================


class TestAggregationIntegration:
    """Integration tests for aggregation combinations."""

    @pytest.mark.os_agnostic
    def test_nested_terms_with_filter_aggregation(self) -> None:
        """Test TermsAggregation with nested FilterAggregation."""
        inner_aggregation = FilterAggregation(
            name="active-only",
            filter=[EqualsFilter(field="active", value=True)],
            aggregation=AvgAggregation(name="avg-price", field="price"),
        )
        outer_aggregation = TermsAggregation(
            name="manufacturers-with-active-avg",
            field="manufacturerId",
            aggregation=inner_aggregation,
        )
        assert outer_aggregation.aggregation is not None
        assert outer_aggregation.aggregation.type == "filter"

    @pytest.mark.os_agnostic
    def test_filter_aggregation_fixture(self, filter_aggregation: FilterAggregation) -> None:
        """Test using the filter_aggregation fixture from conftest.py."""
        assert filter_aggregation.name == "active-price-avg"
        assert len(filter_aggregation.filter) == 1
        assert filter_aggregation.aggregation.type == "avg"
