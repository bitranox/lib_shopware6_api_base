"""Comprehensive tests for helper functions in lib_shopware6_api_base_helpers.py."""

from __future__ import annotations

import io
import sys

import pytest

from lib_shopware6_api_base import Criteria, EqualsFilter
from lib_shopware6_api_base.lib_shopware6_api_base_helpers import (
    _filter_empty,
    _is_not_empty,
    pprint_attrs,
)


# =============================================================================
# TestPprintAttrs - 5 tests
# =============================================================================


class TestPprintAttrs:
    """Tests for the pprint_attrs function."""

    @pytest.mark.os_agnostic
    def test_pprint_attrs_empty_criteria(self) -> None:
        """Test pprint_attrs with empty Criteria outputs empty dict."""
        my_criteria = Criteria()
        # Capture stdout
        captured = io.StringIO()
        sys.stdout = captured
        try:
            pprint_attrs(my_criteria)
        finally:
            sys.stdout = sys.__stdout__
        output = captured.getvalue().strip()
        assert output == "{}"

    @pytest.mark.os_agnostic
    def test_pprint_attrs_criteria_with_limit(self) -> None:
        """Test pprint_attrs with Criteria containing limit."""
        my_criteria = Criteria(limit=10)
        captured = io.StringIO()
        sys.stdout = captured
        try:
            pprint_attrs(my_criteria)
        finally:
            sys.stdout = sys.__stdout__
        output = captured.getvalue().strip()
        assert "limit" in output
        assert "10" in output

    @pytest.mark.os_agnostic
    def test_pprint_attrs_filter(self) -> None:
        """Test pprint_attrs with EqualsFilter."""
        my_filter = EqualsFilter(field="stock", value=10)
        captured = io.StringIO()
        sys.stdout = captured
        try:
            pprint_attrs(my_filter)
        finally:
            sys.stdout = sys.__stdout__
        output = captured.getvalue().strip()
        assert "'field': 'stock'" in output
        assert "'value': 10" in output
        assert "'type': 'equals'" in output

    @pytest.mark.os_agnostic
    def test_pprint_attrs_excludes_none_values(self) -> None:
        """Test pprint_attrs excludes None values from output."""
        my_filter = EqualsFilter(field="stock", value=None)
        captured = io.StringIO()
        sys.stdout = captured
        try:
            pprint_attrs(my_filter)
        finally:
            sys.stdout = sys.__stdout__
        output = captured.getvalue().strip()
        # None values are filtered out by _filter_empty
        assert "'field': 'stock'" in output
        assert "'type': 'equals'" in output

    @pytest.mark.os_agnostic
    def test_pprint_attrs_nested_structure(self) -> None:
        """Test pprint_attrs with nested Criteria structure."""
        my_criteria = Criteria()
        my_criteria.associations["products"] = Criteria(limit=5)
        captured = io.StringIO()
        sys.stdout = captured
        try:
            pprint_attrs(my_criteria)
        finally:
            sys.stdout = sys.__stdout__
        output = captured.getvalue().strip()
        assert "associations" in output
        assert "products" in output
        assert "limit" in output


# =============================================================================
# TestFilterEmpty - 2 tests
# =============================================================================


class TestFilterEmpty:
    """Tests for the _filter_empty helper function."""

    @pytest.mark.os_agnostic
    def test_filter_empty_removes_none_and_empty(self) -> None:
        """Test _filter_empty removes None, empty lists, and empty dicts."""
        data = {
            "name": "test",
            "empty_list": [],
            "empty_dict": {},
            "none_value": None,
            "value": 10,
        }
        filtered = _filter_empty(data)
        assert filtered == {"name": "test", "value": 10}

    @pytest.mark.os_agnostic
    def test_filter_empty_nested_structure(self) -> None:
        """Test _filter_empty handles nested structures."""
        data = {
            "outer": {
                "keep": "value",
                "remove_empty": [],
                "remove_none": None,
                "nested": {
                    "deep_keep": "deep_value",
                    "deep_remove": {},
                },
            },
            "list_with_items": [
                {"item": "value", "empty": []},
                {"item2": "value2"},
            ],
        }
        filtered = _filter_empty(data)
        assert filtered["outer"]["keep"] == "value"
        assert "remove_empty" not in filtered["outer"]
        assert "remove_none" not in filtered["outer"]
        assert filtered["outer"]["nested"]["deep_keep"] == "deep_value"
        assert "deep_remove" not in filtered["outer"]["nested"]
        # Lists are preserved with their items filtered
        assert len(filtered["list_with_items"]) == 2


# =============================================================================
# TestIsNotEmpty - 1 test
# =============================================================================


class TestIsNotEmpty:
    """Tests for the _is_not_empty helper function (backward compatibility)."""

    @pytest.mark.os_agnostic
    def test_is_not_empty_functionality(self) -> None:
        """Test _is_not_empty returns correct boolean values."""
        # The attribute parameter is not used in the current implementation
        # It's kept for backward compatibility with attrs-style filtering
        assert _is_not_empty(None, "value") is True
        assert _is_not_empty(None, 10) is True
        assert _is_not_empty(None, [1, 2, 3]) is True
        assert _is_not_empty(None, {"key": "value"}) is True
        assert _is_not_empty(None, []) is False
        assert _is_not_empty(None, {}) is False
