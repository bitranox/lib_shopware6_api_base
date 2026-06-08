"""Tests for the configuration model and lib_layered_config loading.

Covers:
- ConfShopware6ApiBase construction (field names, [shopware] TOML aliases, defaults)
- grant_type parsing from strings/enum
- load_config_from_env / require_config_from_env via lib_layered_config
"""

from __future__ import annotations

import pytest

from lib_shopware6_api_base.conf_shopware6_api_base_classes import (
    ConfigurationError,
    ConfShopware6ApiBase,
    GrantType,
    load_config_from_env,
    require_config_from_env,
)
from lib_shopware6_api_base.config import get_config


class TestGrantTypeParsing:
    """grant_type field validation and parsing."""

    @pytest.mark.os_agnostic
    def test_grant_type_from_enum(self) -> None:
        assert ConfShopware6ApiBase(grant_type=GrantType.USER_CREDENTIALS).grant_type == GrantType.USER_CREDENTIALS
        assert ConfShopware6ApiBase(grant_type=GrantType.RESOURCE_OWNER).grant_type == GrantType.RESOURCE_OWNER

    @pytest.mark.os_agnostic
    def test_grant_type_from_lowercase_string(self) -> None:
        assert ConfShopware6ApiBase(grant_type="user_credentials").grant_type == GrantType.USER_CREDENTIALS  # type: ignore[arg-type]
        assert ConfShopware6ApiBase(grant_type="resource_owner").grant_type == GrantType.RESOURCE_OWNER  # type: ignore[arg-type]

    @pytest.mark.os_agnostic
    def test_grant_type_from_uppercase_string(self) -> None:
        assert ConfShopware6ApiBase(grant_type="USER_CREDENTIALS").grant_type == GrantType.USER_CREDENTIALS  # type: ignore[arg-type]
        assert ConfShopware6ApiBase(grant_type="RESOURCE_OWNER").grant_type == GrantType.RESOURCE_OWNER  # type: ignore[arg-type]

    @pytest.mark.os_agnostic
    def test_grant_type_invalid_raises_error(self) -> None:
        with pytest.raises(ValueError, match="Invalid grant_type"):
            ConfShopware6ApiBase(grant_type="oauth2")  # type: ignore[arg-type]


class TestConfigModel:
    """ConfShopware6ApiBase model construction and validation."""

    @pytest.mark.os_agnostic
    def test_defaults(self) -> None:
        config = ConfShopware6ApiBase()
        assert config.shopware_admin_api_url == ""
        assert config.shopware_storefront_api_url == ""
        assert config.grant_type == GrantType.USER_CREDENTIALS
        assert config.insecure_transport == "0"
        assert config.follow_redirects is False

    @pytest.mark.os_agnostic
    def test_construct_with_field_names(self) -> None:
        config = ConfShopware6ApiBase(
            shopware_admin_api_url="http://localhost/api",
            username="admin",
            password="shopware",
        )
        assert config.shopware_admin_api_url == "http://localhost/api"
        assert config.username == "admin"

    @pytest.mark.os_agnostic
    def test_construct_with_toml_aliases(self) -> None:
        # The [shopware] TOML keys drop the redundant ``shopware_`` prefix; this is
        # how lib_layered_config feeds the section dict into the model.
        config = ConfShopware6ApiBase.model_validate(
            {"admin_api_url": "http://a/api", "storefront_api_url": "http://s/store-api"}
        )
        assert config.shopware_admin_api_url == "http://a/api"
        assert config.shopware_storefront_api_url == "http://s/store-api"

    @pytest.mark.os_agnostic
    def test_validate_assignment(self) -> None:
        config = ConfShopware6ApiBase()
        config.store_api_sw_access_key = "SWSC123"
        assert config.store_api_sw_access_key == "SWSC123"


class TestLayeredConfigLoading:
    """load_config_from_env / require_config_from_env via lib_layered_config."""

    @pytest.mark.os_agnostic
    def test_load_config_returns_model(self) -> None:
        get_config.cache_clear()
        config = load_config_from_env()
        assert isinstance(config, ConfShopware6ApiBase)

    @pytest.mark.os_agnostic
    def test_env_var_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Environment variables (highest precedence) use the lib_layered_config scheme.
        monkeypatch.setenv("LIB_SHOPWARE6_API_BASE___SHOPWARE__ADMIN_API_URL", "http://env-test/api")
        get_config.cache_clear()
        try:
            config = load_config_from_env()
            assert config.shopware_admin_api_url == "http://env-test/api"
        finally:
            get_config.cache_clear()

    @pytest.mark.os_agnostic
    def test_require_raises_without_config(self, monkeypatch: pytest.MonkeyPatch, tmp_path: object) -> None:
        monkeypatch.delenv("LIB_SHOPWARE6_API_BASE___SHOPWARE__ADMIN_API_URL", raising=False)
        monkeypatch.delenv("LIB_SHOPWARE6_API_BASE___SHOPWARE__STOREFRONT_API_URL", raising=False)
        monkeypatch.chdir(tmp_path)  # type: ignore[arg-type]
        get_config.cache_clear()
        try:
            with pytest.raises(ConfigurationError):
                require_config_from_env()
        finally:
            get_config.cache_clear()


class TestExceptionClasses:
    """Custom exception classes."""

    @pytest.mark.os_agnostic
    def test_configuration_error_is_exception(self) -> None:
        exc = ConfigurationError("test message")
        assert isinstance(exc, Exception)
        assert str(exc) == "test message"

    @pytest.mark.os_agnostic
    def test_configuration_error_can_be_raised(self) -> None:
        with pytest.raises(ConfigurationError, match="config error"):
            raise ConfigurationError("config error")
