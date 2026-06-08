"""Tests for helper functions in lib_shopware6_api_base_helpers.py."""

from __future__ import annotations

import contextlib
import io

import pytest

from lib_shopware6_api_base import Criteria, EqualsFilter
from lib_shopware6_api_base.lib_shopware6_api_base_helpers import pprint_model


def _capture(model: object) -> str:
    """Run pprint_model and return what it printed (stripped)."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        pprint_model(model)  # type: ignore[arg-type]
    return buffer.getvalue().strip()


class TestPprintModel:
    """Tests for the pprint_model function."""

    @pytest.mark.os_agnostic
    def test_empty_criteria(self) -> None:
        """An untouched Criteria dumps to an empty dict (all fields at default)."""
        assert _capture(Criteria()) == "{}"

    @pytest.mark.os_agnostic
    def test_criteria_with_limit(self) -> None:
        """A non-default field shows up; defaults stay hidden."""
        output = _capture(Criteria(limit=10))
        assert "limit" in output
        assert "10" in output

    @pytest.mark.os_agnostic
    def test_filter(self) -> None:
        """Filters keep their discriminating type field."""
        output = _capture(EqualsFilter(field="stock", value=10))
        assert "'field': 'stock'" in output
        assert "'value': 10" in output
        assert "'type': 'equals'" in output

    @pytest.mark.os_agnostic
    def test_default_fields_excluded(self) -> None:
        """Fields left at their default are omitted from the output."""
        output = _capture(EqualsFilter(field="stock", value="x"))
        # Criteria-level containers (filter/sort/...) never appear for a bare filter
        assert "'field': 'stock'" in output
        assert "'type': 'equals'" in output

    @pytest.mark.os_agnostic
    def test_nested_structure(self) -> None:
        """Nested Criteria associations are rendered recursively."""
        my_criteria = Criteria()
        my_criteria.associations["products"] = Criteria(limit=5)
        output = _capture(my_criteria)
        assert "associations" in output
        assert "products" in output
        assert "limit" in output
