"""Comprehensive tests for configuration classes in conf_shopware6_api_base_classes.py."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from lib_shopware6_api_base.conf_shopware6_api_base_classes import (
    ConfShopware6ApiBase,
    GrantType,
    HttpMethod,
    ShopwareAPIError,
)


# =============================================================================
# TestConfShopware6ApiBase - 12 tests
# =============================================================================


class TestConfShopware6ApiBase:
    """Tests for the ConfShopware6ApiBase configuration class."""

    @pytest.mark.os_agnostic
    def test_conf_empty_initialization(self) -> None:
        """Test ConfShopware6ApiBase with default empty values."""
        config = ConfShopware6ApiBase()
        assert config.shopware_admin_api_url == ""
        assert config.shopware_storefront_api_url == ""
        assert config.username == ""
        assert config.password == ""
        assert config.client_id == ""
        assert config.client_secret == ""
        assert config.grant_type == GrantType.USER_CREDENTIALS
        assert config.store_api_sw_access_key == ""

    @pytest.mark.os_agnostic
    def test_conf_with_admin_api_url(self) -> None:
        """Test ConfShopware6ApiBase with admin API URL."""
        config = ConfShopware6ApiBase(shopware_admin_api_url="https://shop.example.com/api")
        assert config.shopware_admin_api_url == "https://shop.example.com/api"

    @pytest.mark.os_agnostic
    def test_conf_with_storefront_api_url(self) -> None:
        """Test ConfShopware6ApiBase with storefront API URL."""
        config = ConfShopware6ApiBase(shopware_storefront_api_url="https://shop.example.com/store-api")
        assert config.shopware_storefront_api_url == "https://shop.example.com/store-api"

    @pytest.mark.os_agnostic
    def test_conf_with_user_credentials(self) -> None:
        """Test ConfShopware6ApiBase with username and password."""
        config = ConfShopware6ApiBase(
            username="admin",
            password="secret123",
        )
        assert config.username == "admin"
        assert config.password == "secret123"

    @pytest.mark.os_agnostic
    def test_conf_with_client_credentials(self) -> None:
        """Test ConfShopware6ApiBase with client ID and secret."""
        config = ConfShopware6ApiBase(
            client_id="integration_client",
            client_secret="integration_secret",
        )
        assert config.client_id == "integration_client"
        assert config.client_secret == "integration_secret"

    @pytest.mark.os_agnostic
    def test_conf_with_user_credentials_grant_type(self) -> None:
        """Test ConfShopware6ApiBase with USER_CREDENTIALS grant type."""
        config = ConfShopware6ApiBase(
            grant_type=GrantType.USER_CREDENTIALS,
        )
        assert config.grant_type == GrantType.USER_CREDENTIALS
        assert config.grant_type.value == "user_credentials"

    @pytest.mark.os_agnostic
    def test_conf_with_resource_owner_grant_type(self) -> None:
        """Test ConfShopware6ApiBase with RESOURCE_OWNER grant type."""
        config = ConfShopware6ApiBase(
            grant_type=GrantType.RESOURCE_OWNER,
        )
        assert config.grant_type == GrantType.RESOURCE_OWNER
        assert config.grant_type.value == "resource_owner"

    @pytest.mark.os_agnostic
    def test_conf_with_store_api_access_key(self) -> None:
        """Test ConfShopware6ApiBase with store API access key."""
        config = ConfShopware6ApiBase(store_api_sw_access_key="SWSC1234567890ABCDEF")
        assert config.store_api_sw_access_key == "SWSC1234567890ABCDEF"

    @pytest.mark.os_agnostic
    def test_conf_full_configuration(self) -> None:
        """Test ConfShopware6ApiBase with all fields populated."""
        config = ConfShopware6ApiBase(
            shopware_admin_api_url="https://shop.example.com/api",
            shopware_storefront_api_url="https://shop.example.com/store-api",
            username="admin",
            password="secret123",
            client_id="test_client_id",
            client_secret="test_client_secret",
            grant_type=GrantType.USER_CREDENTIALS,
            store_api_sw_access_key="SWSC1234567890ABCDEF",
        )
        assert config.shopware_admin_api_url == "https://shop.example.com/api"
        assert config.shopware_storefront_api_url == "https://shop.example.com/store-api"
        assert config.username == "admin"
        assert config.password == "secret123"
        assert config.client_id == "test_client_id"
        assert config.client_secret == "test_client_secret"
        assert config.grant_type == GrantType.USER_CREDENTIALS
        assert config.store_api_sw_access_key == "SWSC1234567890ABCDEF"

    @pytest.mark.os_agnostic
    def test_conf_validate_assignment(self) -> None:
        """Test ConfShopware6ApiBase validates assignment."""
        config = ConfShopware6ApiBase()
        # Should be able to update values after creation
        config.shopware_admin_api_url = "https://new.example.com/api"
        assert config.shopware_admin_api_url == "https://new.example.com/api"

    @pytest.mark.os_agnostic
    def test_conf_fixture_empty(self, empty_config: ConfShopware6ApiBase) -> None:
        """Test using the empty_config fixture."""
        assert empty_config.shopware_admin_api_url == ""
        assert empty_config.grant_type == GrantType.USER_CREDENTIALS

    @pytest.mark.os_agnostic
    def test_conf_fixture_full(self, full_config: ConfShopware6ApiBase) -> None:
        """Test using the full_config fixture."""
        assert full_config.shopware_admin_api_url == "https://shop.example.com/api"
        assert full_config.username == "admin"
        assert full_config.grant_type == GrantType.USER_CREDENTIALS


# =============================================================================
# TestGrantType - 3 tests
# =============================================================================


class TestGrantType:
    """Tests for the GrantType enum."""

    @pytest.mark.os_agnostic
    def test_grant_type_user_credentials(self) -> None:
        """Test GrantType.USER_CREDENTIALS value."""
        assert GrantType.USER_CREDENTIALS == "user_credentials"
        assert GrantType.USER_CREDENTIALS.value == "user_credentials"

    @pytest.mark.os_agnostic
    def test_grant_type_resource_owner(self) -> None:
        """Test GrantType.RESOURCE_OWNER value."""
        assert GrantType.RESOURCE_OWNER == "resource_owner"
        assert GrantType.RESOURCE_OWNER.value == "resource_owner"

    @pytest.mark.os_agnostic
    def test_grant_type_count(self) -> None:
        """Test GrantType enum has exactly 2 values."""
        assert len(GrantType) == 2


# =============================================================================
# TestHttpMethod - 3 tests
# =============================================================================


class TestHttpMethod:
    """Tests for the HttpMethod enum."""

    @pytest.mark.os_agnostic
    def test_http_method_values(self) -> None:
        """Test HttpMethod enum has correct values."""
        assert HttpMethod.GET == "get"
        assert HttpMethod.PATCH == "patch"
        assert HttpMethod.POST == "post"
        assert HttpMethod.PUT == "put"
        assert HttpMethod.DELETE == "delete"

    @pytest.mark.os_agnostic
    def test_http_method_count(self) -> None:
        """Test HttpMethod enum has exactly 5 values."""
        assert len(HttpMethod) == 5

    @pytest.mark.os_agnostic
    def test_http_method_iteration(self) -> None:
        """Test HttpMethod enum can be iterated."""
        methods = list(HttpMethod)
        assert len(methods) == 5
        assert HttpMethod.GET in methods
        assert HttpMethod.POST in methods


# =============================================================================
# TestShopwareAPIError - 2 tests
# =============================================================================


class TestShopwareAPIError:
    """Tests for the ShopwareAPIError exception class."""

    @pytest.mark.os_agnostic
    def test_shopware_api_error_creation(self) -> None:
        """Test ShopwareAPIError can be created with message."""
        error = ShopwareAPIError("Test error message")
        assert str(error) == "Test error message"

    @pytest.mark.os_agnostic
    def test_shopware_api_error_is_base_exception(self) -> None:
        """Test ShopwareAPIError inherits from BaseException."""
        error = ShopwareAPIError("Test error")
        assert isinstance(error, BaseException)
