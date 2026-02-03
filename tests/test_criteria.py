"""Comprehensive tests for Query and Criteria classes in lib_shopware6_api_base_criteria.py."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from lib_shopware6_api_base import (
    AscFieldSorting,
    AvgAggregation,
    ContainsFilter,
    Criteria,
    DescFieldSorting,
    EqualsFilter,
    FieldSorting,
    FilterAggregation,
    Query,
    RangeFilter,
)

# =============================================================================
# TestQuery - 4 tests
# =============================================================================


class TestQuery:
    """Tests for the Query class."""

    @pytest.mark.os_agnostic
    def test_query_with_contains_filter(self) -> None:
        """Test Query with ContainsFilter."""
        my_query = Query(
            score=500,
            query=ContainsFilter(field="name", value="Bronze"),
        )
        assert my_query.score == 500
        assert my_query.query.field == "name"  # type: ignore[union-attr]
        assert my_query.query.type == "contains"

    @pytest.mark.os_agnostic
    def test_query_with_equals_filter(self) -> None:
        """Test Query with EqualsFilter."""
        my_query = Query(
            score=100,
            query=EqualsFilter(field="active", value=True),
        )
        assert my_query.score == 100
        assert my_query.query.value is True  # type: ignore[union-attr]

    @pytest.mark.os_agnostic
    def test_query_model_dump(self) -> None:
        """Test Query model_dump output."""
        my_query = Query(
            score=250,
            query=EqualsFilter(field="manufacturerId", value="abc123"),
        )
        data = my_query.model_dump()
        assert data["score"] == 250
        assert data["query"]["field"] == "manufacturerId"
        assert data["query"]["value"] == "abc123"
        assert data["query"]["type"] == "equals"

    @pytest.mark.os_agnostic
    def test_query_in_criteria(self) -> None:
        """Test Query used within Criteria."""
        my_criteria = Criteria(
            query=[
                Query(score=500, query=ContainsFilter(field="name", value="Bronze")),
                Query(score=500, query=EqualsFilter(field="active", value="true")),
                Query(
                    score=100,
                    query=EqualsFilter(field="manufacturerId", value="db3c17b1e572432eb4a4c881b6f9d68f"),
                ),
            ]
        )
        assert len(my_criteria.query) == 3
        assert my_criteria.query[0].score == 500
        assert my_criteria.query[2].score == 100


# =============================================================================
# TestCriteria - 21 tests
# =============================================================================


class TestCriteria:
    """Tests for the Criteria class."""

    @pytest.mark.os_agnostic
    def test_criteria_empty_initialization(self) -> None:
        """Test Criteria with no parameters returns empty dict."""
        my_criteria = Criteria()
        data = my_criteria.get_dict()
        assert data == {}

    @pytest.mark.os_agnostic
    def test_criteria_with_limit_and_page(self) -> None:
        """Test Criteria with limit and page."""
        my_criteria = Criteria(limit=10, page=1)
        assert my_criteria.limit == 10
        assert my_criteria.page == 1
        data = my_criteria.get_dict()
        assert data["limit"] == 10
        assert data["page"] == 1

    @pytest.mark.os_agnostic
    def test_criteria_with_ids(self) -> None:
        """Test Criteria with ids."""
        ids = [
            "012cd563cf8e4f0384eed93b5201cc98",
            "075fb241b769444bb72431f797fd5776",
            "090fcc2099794771935acf814e3fdb24",
        ]
        my_criteria = Criteria(ids=ids)
        assert my_criteria.ids == ids
        data = my_criteria.get_dict()
        assert data["ids"] == ids

    @pytest.mark.os_agnostic
    def test_criteria_limit_and_ids_mutual_exclusivity(self) -> None:
        """Test Criteria raises ValidationError when both limit and ids are set."""
        with pytest.raises(ValidationError) as exc_info:
            Criteria(
                limit=5,
                ids=["id1", "id2", "id3"],
            )
        assert "limit" in str(exc_info.value).lower() or "ids" in str(exc_info.value).lower()

    @pytest.mark.os_agnostic
    def test_criteria_with_filter(self) -> None:
        """Test Criteria with filter list."""
        my_criteria = Criteria(
            filter=[
                EqualsFilter(field="active", value=True),
                ContainsFilter(field="name", value="Premium"),
            ]
        )
        assert len(my_criteria.filter) == 2
        data = my_criteria.get_dict()
        assert len(data["filter"]) == 2
        assert data["filter"][0]["type"] == "equals"
        assert data["filter"][1]["type"] == "contains"

    @pytest.mark.os_agnostic
    def test_criteria_append_filters(self) -> None:
        """Test appending filters to Criteria."""
        my_criteria = Criteria()
        my_criteria.filter.append(EqualsFilter(field="a", value="a"))
        my_criteria.filter.append(EqualsFilter(field="b", value="b"))
        my_criteria.filter.append(EqualsFilter(field="c", value="c"))
        assert len(my_criteria.filter) == 3

    @pytest.mark.os_agnostic
    def test_criteria_with_aggregation(self) -> None:
        """Test Criteria with aggregations."""
        my_criteria = Criteria(
            limit=1,
            aggregations=[AvgAggregation(name="average-price", field="price")],
        )
        my_criteria.includes["product"] = ["id", "name"]
        data = my_criteria.get_dict()
        assert len(data["aggregations"]) == 1
        assert data["aggregations"][0]["type"] == "avg"
        assert data["includes"]["product"] == ["id", "name"]

    @pytest.mark.os_agnostic
    def test_criteria_with_filter_aggregation(self) -> None:
        """Test Criteria with FilterAggregation."""
        my_criteria = Criteria(
            limit=1,
            includes={"product": ["id", "name"]},
            aggregations=[
                FilterAggregation(
                    name="active-price-avg",
                    filter=[EqualsFilter(field="active", value=True)],
                    aggregation=AvgAggregation(name="avg-price", field="price"),
                )
            ],
        )
        data = my_criteria.get_dict()
        assert data["aggregations"][0]["type"] == "filter"
        assert data["aggregations"][0]["aggregation"]["type"] == "avg"

    @pytest.mark.os_agnostic
    def test_criteria_with_associations(self) -> None:
        """Test Criteria with nested associations."""
        my_criteria = Criteria()
        my_criteria.associations["products"] = Criteria(
            limit=5,
            filter=[EqualsFilter(field="active", value="true")],
        )
        data = my_criteria.get_dict()
        assert "products" in data["associations"]
        assert data["associations"]["products"]["limit"] == 5

    @pytest.mark.os_agnostic
    def test_criteria_nested_associations(self) -> None:
        """Test Criteria with deeply nested associations."""
        my_criteria = Criteria()
        inner_criteria = Criteria(limit=10)
        inner_criteria.associations["manufacturer"] = Criteria(limit=1)
        my_criteria.associations["products"] = inner_criteria

        data = my_criteria.get_dict()
        assert "products" in data["associations"]
        assert "manufacturer" in data["associations"]["products"]["associations"]

    @pytest.mark.os_agnostic
    def test_criteria_with_includes(self) -> None:
        """Test Criteria with includes."""
        my_criteria = Criteria()
        my_criteria.includes["product"] = ["id", "name", "price"]
        my_criteria.includes["manufacturer"] = ["id", "name"]
        data = my_criteria.get_dict()
        assert data["includes"]["product"] == ["id", "name", "price"]
        assert data["includes"]["manufacturer"] == ["id", "name"]

    @pytest.mark.os_agnostic
    def test_criteria_with_grouping(self) -> None:
        """Test Criteria with grouping."""
        my_criteria = Criteria(limit=5, grouping=["active", "manufacturerId"])
        data = my_criteria.get_dict()
        assert data["grouping"] == ["active", "manufacturerId"]

    @pytest.mark.os_agnostic
    def test_criteria_with_sorting(self) -> None:
        """Test Criteria with sorting."""
        my_criteria = Criteria(
            limit=5,
            sort=[
                FieldSorting(field="name", order="ASC", naturalSorting=True),
                DescFieldSorting(field="active"),
            ],
        )
        data = my_criteria.get_dict()
        assert len(data["sort"]) == 2
        assert data["sort"][0]["order"] == "ASC"
        assert data["sort"][0]["naturalSorting"] is True
        assert data["sort"][1]["order"] == "DESC"

    @pytest.mark.os_agnostic
    def test_criteria_with_term(self) -> None:
        """Test Criteria with term search."""
        my_criteria = Criteria(term="search query")
        data = my_criteria.get_dict()
        assert data["term"] == "search query"

    @pytest.mark.os_agnostic
    def test_criteria_with_total_count_mode(self) -> None:
        """Test Criteria with total_count_mode."""
        my_criteria = Criteria(limit=10, total_count_mode=1)
        data = my_criteria.get_dict()
        assert data["total_count_mode"] == 1

    @pytest.mark.os_agnostic
    def test_criteria_get_dict_excludes_empty(self) -> None:
        """Test Criteria.get_dict() excludes None, empty lists, and empty dicts."""
        my_criteria = Criteria(limit=5)
        data = my_criteria.get_dict()
        # Should only have limit, not empty fields
        assert "limit" in data
        assert "filter" not in data  # Empty list excluded
        assert "aggregations" not in data  # Empty list excluded
        assert "associations" not in data  # Empty dict excluded

    @pytest.mark.os_agnostic
    def test_criteria_model_rebuild_resolves_forward_refs(self) -> None:
        """Test that Criteria model_rebuild resolves forward references."""
        # This test verifies that nested Criteria works properly
        outer = Criteria()
        outer.associations["test"] = Criteria(limit=1)
        # If forward refs weren't resolved, this would fail
        data = outer.get_dict()
        assert data["associations"]["test"]["limit"] == 1

    @pytest.mark.os_agnostic
    def test_criteria_complex_query(self) -> None:
        """Test complex Criteria with multiple features."""
        my_criteria = Criteria(
            limit=10,
            page=1,
            filter=[
                EqualsFilter(field="active", value=True),
                RangeFilter(field="price", parameters={"gte": 10, "lte": 100}),
            ],
            aggregations=[AvgAggregation(name="avg-price", field="price")],
            sort=[AscFieldSorting(field="name")],
        )
        my_criteria.includes["product"] = ["id", "name", "price"]

        data = my_criteria.get_dict()
        assert data["limit"] == 10
        assert data["page"] == 1
        assert len(data["filter"]) == 2
        assert len(data["aggregations"]) == 1
        assert len(data["sort"]) == 1
        assert "product" in data["includes"]

    @pytest.mark.os_agnostic
    def test_criteria_default_factory_isolation(self) -> None:
        """Test that default factories create isolated instances."""
        criteria1 = Criteria()
        criteria2 = Criteria()
        criteria1.filter.append(EqualsFilter(field="test", value=1))
        # criteria2 should not be affected
        assert len(criteria2.filter) == 0

    @pytest.mark.os_agnostic
    def test_criteria_with_post_filter_placeholder(self) -> None:
        """Test Criteria with post_filter (not implemented, but field exists)."""
        my_criteria = Criteria()
        # post_filter exists but is not implemented
        assert my_criteria.post_filter == []
        my_criteria.post_filter.append({"placeholder": "value"})
        assert len(my_criteria.post_filter) == 1

    @pytest.mark.os_agnostic
    def test_criteria_fixture_usage(self, complex_criteria: Criteria) -> None:
        """Test using the complex_criteria fixture from conftest.py."""
        assert complex_criteria.limit == 10
        assert complex_criteria.page == 1
        assert len(complex_criteria.filter) == 1
        assert len(complex_criteria.aggregations) == 1
        assert len(complex_criteria.sort) == 1
