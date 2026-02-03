"""Comprehensive tests for sorting classes in lib_shopware6_api_base_criteria_sorting.py."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from lib_shopware6_api_base import (
    AscFieldSorting,
    DescFieldSorting,
    FieldSorting,
)

# =============================================================================
# TestFieldSorting - 4 tests
# =============================================================================


class TestFieldSorting:
    """Tests for the FieldSorting class."""

    @pytest.mark.os_agnostic
    def test_field_sorting_asc_with_natural(self) -> None:
        """Test FieldSorting with ASC order and naturalSorting."""
        my_sorting = FieldSorting(field="name", order="ASC", naturalSorting=True)
        assert my_sorting.field == "name"
        assert my_sorting.order == "ASC"
        assert my_sorting.naturalSorting is True

    @pytest.mark.os_agnostic
    def test_field_sorting_desc_without_natural(self) -> None:
        """Test FieldSorting with DESC order and no naturalSorting."""
        my_sorting = FieldSorting(field="price", order="DESC")
        assert my_sorting.field == "price"
        assert my_sorting.order == "DESC"
        assert my_sorting.naturalSorting is None

    @pytest.mark.os_agnostic
    def test_field_sorting_invalid_order_raises_error(self) -> None:
        """Test FieldSorting raises ValidationError for invalid order."""
        with pytest.raises(ValidationError) as exc_info:
            FieldSorting(field="name", order="INVALID")  # type: ignore[arg-type]
        assert "Input should be 'ASC' or 'DESC'" in str(exc_info.value)

    @pytest.mark.os_agnostic
    def test_field_sorting_model_dump(self) -> None:
        """Test FieldSorting model_dump output."""
        my_sorting = FieldSorting(field="name", order="ASC", naturalSorting=True)
        data = my_sorting.model_dump()
        assert data == {"field": "name", "order": "ASC", "naturalSorting": True}


# =============================================================================
# TestAscFieldSorting - 4 tests
# =============================================================================


class TestAscFieldSorting:
    """Tests for the AscFieldSorting class."""

    @pytest.mark.os_agnostic
    def test_asc_field_sorting_basic(self) -> None:
        """Test AscFieldSorting defaults to ASC order."""
        my_sorting = AscFieldSorting(field="name")
        assert my_sorting.field == "name"
        assert my_sorting.order == "ASC"
        assert my_sorting.naturalSorting is None

    @pytest.mark.os_agnostic
    def test_asc_field_sorting_with_natural(self) -> None:
        """Test AscFieldSorting with naturalSorting enabled."""
        my_sorting = AscFieldSorting(field="name", naturalSorting=True)
        assert my_sorting.field == "name"
        assert my_sorting.order == "ASC"
        assert my_sorting.naturalSorting is True

    @pytest.mark.os_agnostic
    def test_asc_field_sorting_order_is_computed(self) -> None:
        """Test that order is a computed field and always returns ASC."""
        my_sorting = AscFieldSorting(field="test")
        # The order is computed, so it should always be ASC
        assert my_sorting.order == "ASC"

    @pytest.mark.os_agnostic
    def test_asc_field_sorting_model_dump(self) -> None:
        """Test AscFieldSorting model_dump output."""
        my_sorting = AscFieldSorting(field="name", naturalSorting=True)
        data = my_sorting.model_dump()
        assert data == {"field": "name", "naturalSorting": True, "order": "ASC"}


# =============================================================================
# TestDescFieldSorting - 4 tests
# =============================================================================


class TestDescFieldSorting:
    """Tests for the DescFieldSorting class."""

    @pytest.mark.os_agnostic
    def test_desc_field_sorting_basic(self) -> None:
        """Test DescFieldSorting defaults to DESC order."""
        my_sorting = DescFieldSorting(field="price")
        assert my_sorting.field == "price"
        assert my_sorting.order == "DESC"
        assert my_sorting.naturalSorting is None

    @pytest.mark.os_agnostic
    def test_desc_field_sorting_with_natural(self) -> None:
        """Test DescFieldSorting with naturalSorting enabled."""
        my_sorting = DescFieldSorting(field="name", naturalSorting=True)
        assert my_sorting.field == "name"
        assert my_sorting.order == "DESC"
        assert my_sorting.naturalSorting is True

    @pytest.mark.os_agnostic
    def test_desc_field_sorting_order_is_computed(self) -> None:
        """Test that order is a computed field and always returns DESC."""
        my_sorting = DescFieldSorting(field="test")
        # The order is computed, so it should always be DESC
        assert my_sorting.order == "DESC"

    @pytest.mark.os_agnostic
    def test_desc_field_sorting_model_dump(self) -> None:
        """Test DescFieldSorting model_dump output."""
        my_sorting = DescFieldSorting(field="price", naturalSorting=False)
        data = my_sorting.model_dump()
        assert data == {"field": "price", "naturalSorting": False, "order": "DESC"}


# =============================================================================
# Additional Sorting Tests using Fixtures
# =============================================================================


class TestSortingFixtures:
    """Tests using sorting fixtures from conftest.py."""

    @pytest.mark.os_agnostic
    def test_field_sorting_asc_fixture(self, field_sorting_asc: FieldSorting) -> None:
        """Test using the field_sorting_asc fixture."""
        assert field_sorting_asc.field == "name"
        assert field_sorting_asc.order == "ASC"
        assert field_sorting_asc.naturalSorting is True

    @pytest.mark.os_agnostic
    def test_asc_field_sorting_fixture(self, asc_field_sorting: AscFieldSorting) -> None:
        """Test using the asc_field_sorting fixture."""
        assert asc_field_sorting.field == "name"
        assert asc_field_sorting.order == "ASC"
        assert asc_field_sorting.naturalSorting is True

    @pytest.mark.os_agnostic
    def test_desc_field_sorting_fixture(self, desc_field_sorting: DescFieldSorting) -> None:
        """Test using the desc_field_sorting fixture."""
        assert desc_field_sorting.field == "price"
        assert desc_field_sorting.order == "DESC"
        assert desc_field_sorting.naturalSorting is False
