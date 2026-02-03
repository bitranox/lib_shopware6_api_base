"""Comprehensive tests for API client classes in lib_shopware6_api_base.py."""

from __future__ import annotations

from typing import Any

import pytest

from lib_shopware6_api_base import Criteria, EqualsFilter
from lib_shopware6_api_base.conf_shopware6_api_base_classes import (
    ConfShopware6ApiBase,
    GrantType,
)
from lib_shopware6_api_base.lib_shopware6_api_base import (
    HEADER_do_not_fail_on_error,
    HEADER_fail_on_error,
    HEADER_index_asynchronously,
    HEADER_index_disabled,
    HEADER_index_synchronously,
    HEADER_write_in_separate_transactions,
    HEADER_write_in_single_transactions,
    Shopware6AdminAPIClientBase,
    Shopware6StoreFrontClientBase,
    _get_payload_dict,
    _is_type_bytes,
    _is_type_criteria,
)

# =============================================================================
# TestShopware6AdminAPIClientBase - 5 tests
# =============================================================================


class TestShopware6AdminAPIClientBase:
    """Tests for the Shopware6AdminAPIClientBase class."""

    @pytest.mark.os_agnostic
    def test_admin_client_initialization(self, full_config: ConfShopware6ApiBase) -> None:
        """Test Shopware6AdminAPIClientBase initialization with config."""
        client = Shopware6AdminAPIClientBase(config=full_config)
        assert client.config is full_config
        assert client.token == {}

    @pytest.mark.os_agnostic
    def test_admin_client_format_api_url(self, full_config: ConfShopware6ApiBase) -> None:
        """Test _format_admin_api_url method."""
        client = Shopware6AdminAPIClientBase(config=full_config)
        url = client._format_admin_api_url("oauth/token")
        assert url == "https://shop.example.com/api/oauth/token"

    @pytest.mark.os_agnostic
    def test_admin_client_format_api_url_strips_leading_slash(self, full_config: ConfShopware6ApiBase) -> None:
        """Test _format_admin_api_url strips leading slash."""
        client = Shopware6AdminAPIClientBase(config=full_config)
        url = client._format_admin_api_url("/oauth/token")
        assert url == "https://shop.example.com/api/oauth/token"

    @pytest.mark.os_agnostic
    def test_admin_client_get_headers_json(self) -> None:
        """Test _get_headers returns correct JSON headers."""
        headers = Shopware6AdminAPIClientBase._get_headers(content_type="json")
        assert headers == {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @pytest.mark.os_agnostic
    def test_admin_client_get_headers_octet_stream(self) -> None:
        """Test _get_headers returns correct octet-stream headers."""
        headers = Shopware6AdminAPIClientBase._get_headers(content_type="octet-stream")
        assert headers == {
            "Content-Type": "application/octet-stream",
            "Accept": "application/json",
        }


# =============================================================================
# TestShopware6AdminAPIClientBaseHeaders - 3 tests
# =============================================================================


class TestShopware6AdminAPIClientBaseHeaders:
    """Tests for header update functionality."""

    @pytest.mark.os_agnostic
    def test_admin_client_get_headers_with_update(self) -> None:
        """Test _get_headers with header field updates."""
        headers = Shopware6AdminAPIClientBase._get_headers(
            content_type="json",
            update_header_fields={"custom-header": "custom-value"},
        )
        assert headers["custom-header"] == "custom-value"
        assert headers["Content-Type"] == "application/json"

    @pytest.mark.os_agnostic
    def test_admin_client_get_headers_bulk_operations(self) -> None:
        """Test _get_headers with bulk operation headers."""
        update_fields = {
            **HEADER_index_asynchronously,
            **HEADER_write_in_single_transactions,
        }
        headers = Shopware6AdminAPIClientBase._get_headers(
            content_type="json",
            update_header_fields=update_fields,
        )
        assert headers["indexing-behavior"] == "use-queue-indexing"
        assert headers["single-operation"] == "true"

    @pytest.mark.os_agnostic
    def test_bulk_header_constants(self) -> None:
        """Test bulk operation header constants exist and have correct values."""
        assert HEADER_write_in_separate_transactions == {"single-operation": "false"}
        assert HEADER_write_in_single_transactions == {"single-operation": "true"}
        assert HEADER_index_synchronously == {"indexing-behavior": "null"}
        assert HEADER_index_asynchronously == {"indexing-behavior": "use-queue-indexing"}
        assert HEADER_index_disabled == {"indexing-behavior": "disable-indexing"}
        assert HEADER_fail_on_error == {"fail-on-error": "true"}
        assert HEADER_do_not_fail_on_error == {"fail-on-error": "false"}


# =============================================================================
# TestShopware6AdminAPIClientBaseTokenMethods - 2 tests
# =============================================================================


class TestShopware6AdminAPIClientBaseTokenMethods:
    """Tests for token-related methods."""

    @pytest.mark.os_agnostic
    def test_is_refreshable_token_true(self, full_config: ConfShopware6ApiBase) -> None:
        """Test _is_refreshable_token returns True when refresh_token exists."""
        client = Shopware6AdminAPIClientBase(config=full_config)
        client.token = {"access_token": "abc", "refresh_token": "xyz"}
        assert client._is_refreshable_token() is True

    @pytest.mark.os_agnostic
    def test_is_refreshable_token_false(self, full_config: ConfShopware6ApiBase) -> None:
        """Test _is_refreshable_token returns False when no refresh_token."""
        client = Shopware6AdminAPIClientBase(config=full_config)
        client.token = {"access_token": "abc"}
        assert client._is_refreshable_token() is False


# =============================================================================
# TestShopware6StoreFrontClientBase - 2 tests
# =============================================================================


class TestShopware6StoreFrontClientBase:
    """Tests for the Shopware6StoreFrontClientBase class."""

    @pytest.mark.os_agnostic
    def test_storefront_client_initialization(self, full_config: ConfShopware6ApiBase) -> None:
        """Test Shopware6StoreFrontClientBase initialization with config."""
        client = Shopware6StoreFrontClientBase(config=full_config)
        assert client.config is full_config

    @pytest.mark.os_agnostic
    def test_storefront_client_build_api_url(self, full_config: ConfShopware6ApiBase) -> None:
        """Test _build_storefront_api_url method."""
        client = Shopware6StoreFrontClientBase(config=full_config)
        url = client._build_storefront_api_url("context")
        assert url == "https://shop.example.com/store-api/context"


# =============================================================================
# TestShopware6StoreFrontAPIClientBaseHeaders - 3 tests
# =============================================================================


class TestShopware6StoreFrontAPIClientBaseHeaders:
    """Tests for StoreFront client header functionality."""

    @pytest.mark.os_agnostic
    def test_storefront_get_headers_basic(self, full_config: ConfShopware6ApiBase) -> None:
        """Test _get_headers returns correct headers with access key."""
        client = Shopware6StoreFrontClientBase(config=full_config)
        headers = client._get_headers()
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"
        assert headers["sw-access-key"] == full_config.store_api_sw_access_key

    @pytest.mark.os_agnostic
    def test_storefront_get_headers_with_update(self, full_config: ConfShopware6ApiBase) -> None:
        """Test _get_headers with header field updates."""
        client = Shopware6StoreFrontClientBase(config=full_config)
        headers = client._get_headers(update_header_fields={"custom-header": "value"})
        assert headers["custom-header"] == "value"
        assert headers["sw-access-key"] == full_config.store_api_sw_access_key

    @pytest.mark.os_agnostic
    def test_storefront_get_headers_override_access_key(self, full_config: ConfShopware6ApiBase) -> None:
        """Test _get_headers can override access key."""
        client = Shopware6StoreFrontClientBase(config=full_config)
        headers = client._get_headers(update_header_fields={"sw-access-key": "NEW_KEY"})
        assert headers["sw-access-key"] == "NEW_KEY"


# =============================================================================
# TestHelperFunctions - 4 tests
# =============================================================================


class TestHelperFunctions:
    """Tests for helper functions in lib_shopware6_api_base.py."""

    @pytest.mark.os_agnostic
    def test_is_type_bytes_true(self) -> None:
        """Test _is_type_bytes returns True for bytes."""
        assert _is_type_bytes(b"test data") is True

    @pytest.mark.os_agnostic
    def test_is_type_bytes_false(self) -> None:
        """Test _is_type_bytes returns False for non-bytes."""
        assert _is_type_bytes("test") is False
        assert _is_type_bytes({}) is False
        assert _is_type_bytes(None) is False

    @pytest.mark.os_agnostic
    def test_is_type_criteria_true(self) -> None:
        """Test _is_type_criteria returns True for Criteria."""
        assert _is_type_criteria(Criteria()) is True
        assert _is_type_criteria(Criteria(limit=10)) is True

    @pytest.mark.os_agnostic
    def test_is_type_criteria_false(self) -> None:
        """Test _is_type_criteria returns False for non-Criteria."""
        assert _is_type_criteria({}) is False
        assert _is_type_criteria(None) is False
        assert _is_type_criteria("test") is False


# =============================================================================
# TestGetPayloadDict - 3 tests
# =============================================================================


class TestGetPayloadDict:
    """Tests for _get_payload_dict function."""

    @pytest.mark.os_agnostic
    def test_get_payload_dict_from_none(self) -> None:
        """Test _get_payload_dict returns empty dict for None."""
        result = _get_payload_dict(None)
        assert result == {}

    @pytest.mark.os_agnostic
    def test_get_payload_dict_from_dict(self) -> None:
        """Test _get_payload_dict returns dict as-is."""
        payload: dict[str, Any] = {"key": "value", "limit": 10}
        result = _get_payload_dict(payload)
        assert result == payload

    @pytest.mark.os_agnostic
    def test_get_payload_dict_from_criteria(self) -> None:
        """Test _get_payload_dict converts Criteria to dict."""
        criteria = Criteria(limit=10, page=1)
        criteria.filter.append(EqualsFilter(field="active", value=True))
        result = _get_payload_dict(criteria)
        assert result["limit"] == 10
        assert result["page"] == 1
        assert len(result["filter"]) == 1


# =============================================================================
# Integration Tests marked for external services
# =============================================================================


@pytest.mark.integration
class TestShopware6AdminAPIClientBaseIntegration:
    """Integration tests that require a running Shopware instance.

    These tests use the docker_test_config fixture which automatically
    ensures the dockware container is running.
    """

    def test_admin_client_get_token_user_credentials(self, docker_test_config: ConfShopware6ApiBase) -> None:
        """Test getting token with user credentials."""
        client = Shopware6AdminAPIClientBase(config=docker_test_config)
        client._get_access_token_by_user_credentials()
        assert "access_token" in client.token
        assert "refresh_token" in client.token

    def test_admin_client_get_token_resource_owner(self, docker_test_config: ConfShopware6ApiBase) -> None:
        """Test getting token with resource owner credentials.

        Note: docker_test_config fixture already ensures resource owner credentials exist.
        """
        # Create a config for resource owner grant
        config = ConfShopware6ApiBase(
            shopware_admin_api_url=docker_test_config.shopware_admin_api_url,
            client_id=docker_test_config.client_id,
            client_secret=docker_test_config.client_secret,
            grant_type=GrantType.RESOURCE_OWNER,
        )
        client = Shopware6AdminAPIClientBase(config=config)
        client._get_access_token_by_resource_owner()
        assert "access_token" in client.token

    def test_admin_client_request_get(self, docker_test_config: ConfShopware6ApiBase) -> None:
        """Test GET request to admin API."""
        client = Shopware6AdminAPIClientBase(config=docker_test_config)
        response = client.request_get("currency")
        assert "data" in response
        assert isinstance(response["data"], list)

    def test_admin_client_request_get_paginated(self, docker_test_config: ConfShopware6ApiBase) -> None:
        """Test paginated GET request."""
        client = Shopware6AdminAPIClientBase(config=docker_test_config)
        criteria = Criteria(limit=1, page=1)
        response = client.request_get_paginated("currency", payload=criteria)
        assert "data" in response
        assert isinstance(response["data"], list)

    def test_admin_client_request_post(self, docker_test_config: ConfShopware6ApiBase) -> None:
        """Test POST request to admin API (search)."""
        client = Shopware6AdminAPIClientBase(config=docker_test_config)
        criteria = Criteria(limit=5)
        response = client.request_post("search/currency", payload=criteria)
        assert "data" in response
        assert isinstance(response["data"], list)


@pytest.mark.integration
class TestShopware6AdminAPIClientBaseIntegrationAdvanced:
    """Advanced integration tests for Admin API covering PATCH, PUT, DELETE.

    These tests use the docker_test_config fixture which automatically
    ensures the dockware container is running.
    """

    def test_admin_client_crud_operations(self, docker_test_config: ConfShopware6ApiBase) -> None:
        """Test full CRUD cycle: Create, Read, Update (PATCH), Delete a tag."""
        import uuid

        client = Shopware6AdminAPIClientBase(config=docker_test_config)

        # Generate unique test data
        tag_id = uuid.uuid4().hex
        tag_name = f"test-tag-{tag_id[:8]}"

        # CREATE - POST a new tag
        create_payload = {"id": tag_id, "name": tag_name}
        client.request_post("tag", payload=create_payload)

        # READ - GET the created tag (Shopware returns flat structure, not JSON:API)
        response = client.request_get(f"tag/{tag_id}")
        assert response["data"]["id"] == tag_id
        assert response["data"]["name"] == tag_name

        # UPDATE - PATCH the tag
        updated_name = f"updated-{tag_name}"
        patch_payload = {"name": updated_name}
        client.request_patch(f"tag/{tag_id}", payload=patch_payload)

        # Verify update
        response = client.request_get(f"tag/{tag_id}")
        assert response["data"]["name"] == updated_name

        # DELETE - Remove the tag
        client.request_delete(f"tag/{tag_id}")

        # Verify deletion - request should raise an error for non-existent resource
        from lib_shopware6_api_base.conf_shopware6_api_base_classes import ShopwareAPIError

        with pytest.raises(ShopwareAPIError):
            client.request_get(f"tag/{tag_id}")

    def test_admin_client_request_patch(self, docker_test_config: ConfShopware6ApiBase) -> None:
        """Test PATCH request to admin API."""
        import uuid

        client = Shopware6AdminAPIClientBase(config=docker_test_config)

        # Create a tag to patch
        tag_id = uuid.uuid4().hex
        tag_name = f"patch-test-{tag_id[:8]}"
        client.request_post("tag", payload={"id": tag_id, "name": tag_name})

        # PATCH the tag
        new_name = f"patched-{tag_name}"
        patch_response = client.request_patch(f"tag/{tag_id}", payload={"name": new_name})
        # PATCH returns empty dict on success (204 No Content)
        assert isinstance(patch_response, dict)

        # Verify patch worked
        response = client.request_get(f"tag/{tag_id}")
        assert response["data"]["name"] == new_name

        # Clean up
        client.request_delete(f"tag/{tag_id}")

    def test_admin_client_request_delete(self, docker_test_config: ConfShopware6ApiBase) -> None:
        """Test DELETE request to admin API."""
        import uuid

        client = Shopware6AdminAPIClientBase(config=docker_test_config)

        # Create a tag to delete
        tag_id = uuid.uuid4().hex
        tag_name = f"delete-test-{tag_id[:8]}"

        create_payload = {"id": tag_id, "name": tag_name}
        client.request_post("tag", payload=create_payload)

        # DELETE the tag
        delete_response = client.request_delete(f"tag/{tag_id}")
        # DELETE returns empty dict on success (204 No Content)
        assert isinstance(delete_response, dict)

    def test_admin_client_with_custom_headers(self, docker_test_config: ConfShopware6ApiBase) -> None:
        """Test request with custom header fields."""
        client = Shopware6AdminAPIClientBase(config=docker_test_config)

        # Test with indexing behavior header
        custom_headers = {"indexing-behavior": "use-queue-indexing"}
        response = client.request_get("currency", update_header_fields=custom_headers)
        assert "data" in response

    def test_admin_client_search_with_criteria(self, docker_test_config: ConfShopware6ApiBase) -> None:
        """Test search with complex Criteria object."""
        client = Shopware6AdminAPIClientBase(config=docker_test_config)

        # Create criteria with filter, limit, and sorting
        criteria = Criteria(limit=5, page=1)
        criteria.filter.append(EqualsFilter(field="active", value=True))

        response = client.request_post("search/product", payload=criteria)
        assert "data" in response
        assert isinstance(response["data"], list)


@pytest.mark.integration
class TestShopware6StoreFrontAPIClientBaseIntegration:
    """Integration tests for StoreFront API that require a running Shopware instance.

    These tests use the docker_test_config fixture which automatically
    ensures the dockware container is running.
    """

    def test_storefront_client_request_get(self, docker_test_config: ConfShopware6ApiBase) -> None:
        """Test GET request to storefront API.

        Note: docker_test_config fixture already sets up store_api_sw_access_key.
        """
        client = Shopware6StoreFrontClientBase(config=docker_test_config)
        response = client.request_get("context")
        assert "token" in response or "salesChannel" in response

    def test_storefront_client_request_post(self, docker_test_config: ConfShopware6ApiBase) -> None:
        """Test POST request to storefront API.

        Note: docker_test_config fixture already sets up store_api_sw_access_key.
        """
        client = Shopware6StoreFrontClientBase(config=docker_test_config)
        criteria = Criteria(limit=5)
        response = client.request_post("product", payload=criteria)
        assert "elements" in response or "data" in response

    def test_storefront_client_request_get_list(self, docker_test_config: ConfShopware6ApiBase) -> None:
        """Test GET list request to storefront API.

        Note: docker_test_config fixture already sets up store_api_sw_access_key.
        """
        client = Shopware6StoreFrontClientBase(config=docker_test_config)
        response = client.request_get_list("currency")
        assert isinstance(response, list)
