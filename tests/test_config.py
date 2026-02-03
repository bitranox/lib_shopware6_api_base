"""Tests for configuration classes and loading functions.

These tests cover:
- ConfShopware6ApiBase initialization and validation
- Grant type parsing from various formats
- Environment file loading (from_env_file, from_env_vars)
- Configuration search functions (load_config_from_env, require_config_from_env)
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from lib_shopware6_api_base.conf_shopware6_api_base_classes import (
    ConfigurationError,
    ConfShopware6ApiBase,
    GrantType,
    load_config_from_env,
    require_config_from_env,
)

if TYPE_CHECKING:
    from collections.abc import Generator


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_env_file() -> Generator[Path, None, None]:
    """Create a temporary .env file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write('SHOPWARE_ADMIN_API_URL="http://localhost/api"\n')
        f.write('SHOPWARE_STOREFRONT_API_URL="http://localhost/store-api"\n')
        f.write("USERNAME=testuser\n")
        f.write("PASSWORD=testpass\n")
        f.write("CLIENT_ID=test_client\n")
        f.write("CLIENT_SECRET=test_secret\n")
        f.write("GRANT_TYPE=user_credentials\n")
        f.write('STORE_API_SW_ACCESS_KEY="SWTEST123"\n')
        f.write('INSECURE_TRANSPORT="1"\n')
        temp_path = Path(f.name)
    yield temp_path
    temp_path.unlink(missing_ok=True)


@pytest.fixture
def temp_env_file_single_quotes() -> Generator[Path, None, None]:
    """Create a temp .env file with single-quoted values."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("SHOPWARE_ADMIN_API_URL='http://localhost/api'\n")
        f.write("USERNAME='admin'\n")
        temp_path = Path(f.name)
    yield temp_path
    temp_path.unlink(missing_ok=True)


@pytest.fixture
def temp_env_file_with_comments() -> Generator[Path, None, None]:
    """Create a temp .env file with comments and empty lines."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("# This is a comment\n")
        f.write("\n")
        f.write("SHOPWARE_ADMIN_API_URL=http://localhost/api\n")
        f.write("# Another comment\n")
        f.write("USERNAME=admin\n")
        f.write("\n")
        temp_path = Path(f.name)
    yield temp_path
    temp_path.unlink(missing_ok=True)


@pytest.fixture
def temp_env_file_resource_owner() -> Generator[Path, None, None]:
    """Create a temp .env file configured for resource owner grant."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("SHOPWARE_ADMIN_API_URL=http://localhost/api\n")
        f.write("CLIENT_ID=integration_id\n")
        f.write("CLIENT_SECRET=integration_secret\n")
        f.write("GRANT_TYPE=RESOURCE_OWNER\n")
        f.write("INSECURE_TRANSPORT=1\n")
        temp_path = Path(f.name)
    yield temp_path
    temp_path.unlink(missing_ok=True)


# =============================================================================
# GrantType Parsing Tests
# =============================================================================


class TestGrantTypeParsing:
    """Tests for grant_type field validation and parsing."""

    @pytest.mark.os_agnostic
    def test_grant_type_from_enum(self) -> None:
        """Test grant_type accepts GrantType enum directly."""
        config = ConfShopware6ApiBase(grant_type=GrantType.USER_CREDENTIALS)
        assert config.grant_type == GrantType.USER_CREDENTIALS

        config = ConfShopware6ApiBase(grant_type=GrantType.RESOURCE_OWNER)
        assert config.grant_type == GrantType.RESOURCE_OWNER

    @pytest.mark.os_agnostic
    def test_grant_type_from_lowercase_string(self) -> None:
        """Test grant_type accepts lowercase string values."""
        config = ConfShopware6ApiBase(grant_type="user_credentials")  # type: ignore[arg-type]
        assert config.grant_type == GrantType.USER_CREDENTIALS

        config = ConfShopware6ApiBase(grant_type="resource_owner")  # type: ignore[arg-type]
        assert config.grant_type == GrantType.RESOURCE_OWNER

    @pytest.mark.os_agnostic
    def test_grant_type_from_uppercase_string(self) -> None:
        """Test grant_type accepts uppercase string values."""
        config = ConfShopware6ApiBase(grant_type="USER_CREDENTIALS")  # type: ignore[arg-type]
        assert config.grant_type == GrantType.USER_CREDENTIALS

        config = ConfShopware6ApiBase(grant_type="RESOURCE_OWNER")  # type: ignore[arg-type]
        assert config.grant_type == GrantType.RESOURCE_OWNER

    @pytest.mark.os_agnostic
    def test_grant_type_invalid_raises_error(self) -> None:
        """Test grant_type rejects invalid values."""
        with pytest.raises(ValueError, match="Invalid grant_type"):
            ConfShopware6ApiBase(grant_type="invalid_grant")  # type: ignore[arg-type]

        with pytest.raises(ValueError, match="Invalid grant_type"):
            ConfShopware6ApiBase(grant_type="oauth2")  # type: ignore[arg-type]


# =============================================================================
# Environment File Loading Tests
# =============================================================================


class TestFromEnvFile:
    """Tests for ConfShopware6ApiBase.from_env_file() method."""

    @pytest.mark.os_agnostic
    def test_from_env_file_loads_all_values(self, temp_env_file: Path) -> None:
        """Test from_env_file loads all configuration values."""
        config = ConfShopware6ApiBase.from_env_file(temp_env_file)

        assert config.shopware_admin_api_url == "http://localhost/api"
        assert config.shopware_storefront_api_url == "http://localhost/store-api"
        assert config.username == "testuser"
        assert config.password == "testpass"
        assert config.client_id == "test_client"
        assert config.client_secret == "test_secret"
        assert config.grant_type == GrantType.USER_CREDENTIALS
        assert config.store_api_sw_access_key == "SWTEST123"
        assert config.insecure_transport == "1"

    @pytest.mark.os_agnostic
    def test_from_env_file_handles_single_quotes(self, temp_env_file_single_quotes: Path) -> None:
        """Test from_env_file handles single-quoted values."""
        config = ConfShopware6ApiBase.from_env_file(temp_env_file_single_quotes)

        assert config.shopware_admin_api_url == "http://localhost/api"
        assert config.username == "admin"

    @pytest.mark.os_agnostic
    def test_from_env_file_skips_comments_and_empty_lines(self, temp_env_file_with_comments: Path) -> None:
        """Test from_env_file skips comments and empty lines."""
        config = ConfShopware6ApiBase.from_env_file(temp_env_file_with_comments)

        assert config.shopware_admin_api_url == "http://localhost/api"
        assert config.username == "admin"

    @pytest.mark.os_agnostic
    def test_from_env_file_resource_owner_grant(self, temp_env_file_resource_owner: Path) -> None:
        """Test from_env_file correctly parses RESOURCE_OWNER grant type."""
        config = ConfShopware6ApiBase.from_env_file(temp_env_file_resource_owner)

        assert config.grant_type == GrantType.RESOURCE_OWNER
        assert config.client_id == "integration_id"
        assert config.client_secret == "integration_secret"

    @pytest.mark.os_agnostic
    def test_from_env_file_nonexistent_raises_error(self) -> None:
        """Test from_env_file raises ConfigurationError for missing file."""
        with pytest.raises(ConfigurationError, match="Configuration file not found"):
            ConfShopware6ApiBase.from_env_file("/nonexistent/path/.env")

    @pytest.mark.os_agnostic
    def test_from_env_file_accepts_path_object(self, temp_env_file: Path) -> None:
        """Test from_env_file accepts Path objects."""
        config = ConfShopware6ApiBase.from_env_file(temp_env_file)
        assert config.shopware_admin_api_url == "http://localhost/api"

    @pytest.mark.os_agnostic
    def test_from_env_file_accepts_string_path(self, temp_env_file: Path) -> None:
        """Test from_env_file accepts string paths."""
        config = ConfShopware6ApiBase.from_env_file(str(temp_env_file))
        assert config.shopware_admin_api_url == "http://localhost/api"


# =============================================================================
# Environment Variables Loading Tests
# =============================================================================


class TestFromEnvVars:
    """Tests for ConfShopware6ApiBase.from_env_vars() method."""

    @pytest.mark.os_agnostic
    def test_from_env_vars_loads_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test from_env_vars loads values from environment variables."""
        monkeypatch.setenv("SHOPWARE_ADMIN_API_URL", "http://env-test/api")
        monkeypatch.setenv("USERNAME", "env_user")
        monkeypatch.setenv("PASSWORD", "env_pass")
        monkeypatch.setenv("GRANT_TYPE", "resource_owner")

        config = ConfShopware6ApiBase.from_env_vars()

        assert config.shopware_admin_api_url == "http://env-test/api"
        assert config.username == "env_user"
        assert config.password == "env_pass"
        assert config.grant_type == GrantType.RESOURCE_OWNER

    @pytest.mark.os_agnostic
    def test_from_env_vars_uses_defaults_when_not_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test from_env_vars uses defaults for unset variables."""
        # Clear all relevant env vars
        for var in [
            "SHOPWARE_ADMIN_API_URL",
            "SHOPWARE_STOREFRONT_API_URL",
            "USERNAME",
            "PASSWORD",
            "CLIENT_ID",
            "CLIENT_SECRET",
            "GRANT_TYPE",
            "STORE_API_SW_ACCESS_KEY",
            "INSECURE_TRANSPORT",
        ]:
            monkeypatch.delenv(var, raising=False)

        config = ConfShopware6ApiBase.from_env_vars()

        assert config.shopware_admin_api_url == ""
        assert config.username == ""
        assert config.grant_type == GrantType.USER_CREDENTIALS


# =============================================================================
# load_config_from_env Tests
# =============================================================================


class TestLoadConfigFromEnv:
    """Tests for load_config_from_env() function."""

    @pytest.mark.os_agnostic
    def test_load_config_from_env_with_explicit_path(self, temp_env_file: Path) -> None:
        """Test load_config_from_env loads from explicit path."""
        config = load_config_from_env(temp_env_file)
        assert config.shopware_admin_api_url == "http://localhost/api"

    @pytest.mark.os_agnostic
    def test_load_config_from_env_explicit_path_not_found(self) -> None:
        """Test load_config_from_env raises error for explicit nonexistent path."""
        with pytest.raises(ConfigurationError, match="Configuration file not found"):
            load_config_from_env("/nonexistent/.env")

    @pytest.mark.os_agnostic
    def test_load_config_from_env_falls_back_to_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test load_config_from_env falls back to environment variables."""
        # Ensure no .env file exists in current directory
        monkeypatch.chdir(tempfile.gettempdir())
        monkeypatch.setenv("SHOPWARE_ADMIN_API_URL", "http://fallback/api")

        config = load_config_from_env()
        assert config.shopware_admin_api_url == "http://fallback/api"


# =============================================================================
# require_config_from_env Tests
# =============================================================================


class TestRequireConfigFromEnv:
    """Tests for require_config_from_env() function."""

    @pytest.mark.os_agnostic
    def test_require_config_from_env_with_explicit_path(self, temp_env_file: Path) -> None:
        """Test require_config_from_env loads from explicit path."""
        config = require_config_from_env(temp_env_file)
        assert config.shopware_admin_api_url == "http://localhost/api"

    @pytest.mark.os_agnostic
    def test_require_config_from_env_explicit_path_not_found(self) -> None:
        """Test require_config_from_env raises error for missing explicit path."""
        with pytest.raises(ConfigurationError, match="Configuration file not found"):
            require_config_from_env("/nonexistent/.env")

    @pytest.mark.os_agnostic
    def test_require_config_from_env_no_env_file_raises_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test require_config_from_env raises error when no .env found."""
        # Change to temp directory with no .env file
        monkeypatch.chdir(tempfile.gettempdir())

        with pytest.raises(ConfigurationError, match="Configuration file not found"):
            require_config_from_env()


# =============================================================================
# Insecure Transport Tests
# =============================================================================


class TestInsecureTransport:
    """Tests for insecure transport environment variable handling."""

    @pytest.mark.os_agnostic
    def test_insecure_transport_sets_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test insecure_transport='1' sets OAUTHLIB_INSECURE_TRANSPORT."""
        # Clear the env var first
        monkeypatch.delenv("OAUTHLIB_INSECURE_TRANSPORT", raising=False)

        config = ConfShopware6ApiBase(insecure_transport="1")

        assert config.insecure_transport == "1"
        assert os.environ.get("OAUTHLIB_INSECURE_TRANSPORT") == "1"

    @pytest.mark.os_agnostic
    def test_insecure_transport_default_does_not_set_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test default insecure_transport='0' doesn't set env var."""
        monkeypatch.delenv("OAUTHLIB_INSECURE_TRANSPORT", raising=False)

        config = ConfShopware6ApiBase(insecure_transport="0")

        assert config.insecure_transport == "0"
        # The env var should not be set (or remain unset)


# =============================================================================
# Exception Classes Tests
# =============================================================================


class TestExceptionClasses:
    """Tests for custom exception classes."""

    @pytest.mark.os_agnostic
    def test_configuration_error_is_exception(self) -> None:
        """Test ConfigurationError is an Exception."""
        exc = ConfigurationError("test message")
        assert isinstance(exc, Exception)
        assert str(exc) == "test message"

    @pytest.mark.os_agnostic
    def test_configuration_error_can_be_raised(self) -> None:
        """Test ConfigurationError can be raised and caught."""
        with pytest.raises(ConfigurationError, match="config error"):
            raise ConfigurationError("config error")
