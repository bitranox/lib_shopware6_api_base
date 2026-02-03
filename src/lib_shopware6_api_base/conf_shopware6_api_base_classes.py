# STDLIB
import os
from enum import Enum
from pathlib import Path
from typing import Any

# EXT
from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from ._compat import Self

__all__ = [
    "GrantType",
    "HttpMethod",
    "ShopwareAPIError",
    "ConfigurationError",
    "ConfShopware6ApiBase",
    "load_config_from_env",
    "require_config_from_env",
]


class GrantType(str, Enum):
    """OAuth2 grant type for Shopware6 API authentication."""

    USER_CREDENTIALS = "user_credentials"
    RESOURCE_OWNER = "resource_owner"


class HttpMethod(str, Enum):
    """HTTP methods supported by the Shopware6 API."""

    GET = "get"
    PATCH = "patch"
    POST = "post"
    PUT = "put"
    DELETE = "delete"


class ShopwareAPIError(Exception):
    """Exception raised for Shopware API errors."""

    pass


class ConfigurationError(Exception):
    """Exception raised for configuration errors."""

    pass


class ConfShopware6ApiBase(BaseSettings):
    """
    Configuration for Shopware6 API connection.

    This configuration can be loaded from:
    1. Environment variables (with SHOPWARE_ prefix, e.g., SHOPWARE_USERNAME)
    2. A .env file in the current working directory
    3. A custom .env file path via load_config_from_env()

    See example.env for a documented template of all configuration options.

    Environment Variables:
        All environment variables use the SHOPWARE_ prefix to avoid collision
        with system environment variables (e.g., Windows USERNAME):

        - SHOPWARE_ADMIN_API_URL
        - SHOPWARE_STOREFRONT_API_URL
        - SHOPWARE_USERNAME
        - SHOPWARE_PASSWORD
        - SHOPWARE_CLIENT_ID
        - SHOPWARE_CLIENT_SECRET
        - SHOPWARE_GRANT_TYPE
        - SHOPWARE_STORE_API_SW_ACCESS_KEY
        - SHOPWARE_INSECURE_TRANSPORT

    Attributes:
        shopware_admin_api_url: Admin API URL (e.g., 'https://shop.example.com/api')
        shopware_storefront_api_url: Storefront API URL (e.g., 'https://shop.example.com/store-api')
        username: Admin username for User Credentials grant type
        password: Admin password for User Credentials grant type
        client_id: Integration Access ID for Resource Owner grant type
        client_secret: Integration Secret for Resource Owner grant type
        grant_type: OAuth2 grant type (USER_CREDENTIALS or RESOURCE_OWNER)
        store_api_sw_access_key: Store API access key for Storefront API
        insecure_transport: Allow HTTP instead of HTTPS (development only!)

    """

    model_config = SettingsConfigDict(
        env_prefix="SHOPWARE_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_assignment=True,
    )

    # API Endpoints
    # Use validation_alias to avoid double prefix: SHOPWARE_SHOPWARE_ADMIN_API_URL
    shopware_admin_api_url: str = Field(default="", validation_alias=AliasChoices("ADMIN_API_URL", "shopware_admin_api_url"))
    shopware_storefront_api_url: str = Field(
        default="", validation_alias=AliasChoices("STOREFRONT_API_URL", "shopware_storefront_api_url")
    )

    # User Credentials Grant Type (with refresh token)
    # Use for: client applications performing administrative actions
    # Setup: Admin Panel > Settings > System > Users
    username: str = ""
    password: str = ""

    # Resource Owner Grant Type (no refresh token)
    # Use for: machine-to-machine communications, CLI jobs, automated services
    # Setup: Admin Panel > Settings > System > Integrations
    # Docs: https://shopware.stoplight.io/docs/admin-api/ZG9jOjEwODA3NjQx-authentication-and-authorisation
    client_id: str = ""
    client_secret: str = ""

    # Grant type selection
    grant_type: GrantType = GrantType.USER_CREDENTIALS

    # Store API access key
    # Setup: Admin Panel > Sales Channels > [Channel] > API Access
    store_api_sw_access_key: str = ""

    # Security: Allow insecure transport (HTTP instead of HTTPS)
    # WARNING: Only set to "1" for local development/testing!
    insecure_transport: str = "0"

    @field_validator("grant_type", mode="before")
    @classmethod
    def parse_grant_type(cls, v: str | GrantType) -> GrantType:
        """Parse grant_type from string or GrantType enum."""
        if isinstance(v, GrantType):
            return v
        # At this point v is guaranteed to be str
        # Handle both "USER_CREDENTIALS" and "user_credentials" formats
        v_upper = v.upper()
        if v_upper in ("USER_CREDENTIALS", "RESOURCE_OWNER"):
            return GrantType(v.lower())
        # Try direct enum value
        try:
            return GrantType(v.lower())
        except ValueError:
            pass
        raise ValueError(f"Invalid grant_type: {v!r}. Must be 'USER_CREDENTIALS' or 'RESOURCE_OWNER'")

    @model_validator(mode="after")
    def set_insecure_transport_env(self) -> Self:
        """Set OAUTHLIB_INSECURE_TRANSPORT environment variable after initialization."""
        if self.insecure_transport == "1":
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        return self

    @classmethod
    def from_env_file(cls, env_file: str | Path) -> "ConfShopware6ApiBase":
        """
        Load configuration from a specific .env file.

        Args:
            env_file: Path to the .env file

        Returns:
            ConfShopware6ApiBase: Loaded configuration object

        Raises:
            ConfigurationError: If the env_file does not exist

        """
        env_path = Path(env_file)
        if not env_path.exists():
            raise ConfigurationError(
                f"Configuration file not found: {env_path}\n\n"
                f"Please create a .env file with your Shopware 6 API credentials.\n"
                f"See 'example.env' in the project root for a documented template:\n"
                f"  https://github.com/bitranox/lib_shopware6_api_base/blob/master/example.env\n\n"
                f"Quick start:\n"
                f"  1. Copy example.env to .env\n"
                f"  2. Edit .env with your shop's credentials\n"
            )

        # Read and parse the env file manually
        env_values = _parse_env_file(env_path)
        return cls(**env_values)

    @classmethod
    def from_env_vars(cls) -> "ConfShopware6ApiBase":
        """
        Load configuration from environment variables only (no .env file).

        Returns:
            ConfShopware6ApiBase: Configuration loaded from environment variables

        """
        env_values = _get_env_values()
        return cls(**env_values)


def _parse_env_file(env_path: Path) -> dict[str, Any]:
    """Parse a .env file and return a dictionary of values.

    Environment variable names are mapped to Pydantic field names using
    explicit mapping. All env vars use the SHOPWARE_ prefix.
    """
    # Mapping of env var names (uppercase) to pydantic field names (not actual credentials)
    env_to_field = {
        "SHOPWARE_ADMIN_API_URL": "shopware_admin_api_url",
        "SHOPWARE_STOREFRONT_API_URL": "shopware_storefront_api_url",
        "SHOPWARE_USERNAME": "username",
        "SHOPWARE_PASSWORD": "password",  # nosec B105 - field name mapping, not actual password
        "SHOPWARE_CLIENT_ID": "client_id",
        "SHOPWARE_CLIENT_SECRET": "client_secret",  # nosec B105 - field name mapping, not actual secret
        "SHOPWARE_GRANT_TYPE": "grant_type",
        "SHOPWARE_STORE_API_SW_ACCESS_KEY": "store_api_sw_access_key",
        "SHOPWARE_INSECURE_TRANSPORT": "insecure_transport",
    }
    env_values: dict[str, Any] = {}
    with env_path.open(encoding="utf-8") as f:
        for raw_line in f:
            stripped_line = raw_line.strip()
            # Skip empty lines and comments
            if not stripped_line or stripped_line.startswith("#"):
                continue
            # Parse KEY=value or KEY="value"
            if "=" in stripped_line:
                key, _, value = stripped_line.partition("=")
                key = key.strip().upper()  # Normalize to uppercase for lookup
                value = value.strip()
                # Remove surrounding quotes
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                # Map to field name if known, otherwise skip
                if key in env_to_field:
                    env_values[env_to_field[key]] = value
    return env_values


def _get_env_values() -> dict[str, Any]:
    """Get configuration values from environment variables.

    All environment variables use the SHOPWARE_ prefix to avoid collision
    with system environment variables (e.g., Windows USERNAME).
    """
    # Mapping of environment variable names to pydantic field names (not actual credentials)
    env_mapping = {
        "SHOPWARE_ADMIN_API_URL": "shopware_admin_api_url",
        "SHOPWARE_STOREFRONT_API_URL": "shopware_storefront_api_url",
        "SHOPWARE_USERNAME": "username",
        "SHOPWARE_PASSWORD": "password",  # nosec B105 - field name mapping, not actual password
        "SHOPWARE_CLIENT_ID": "client_id",
        "SHOPWARE_CLIENT_SECRET": "client_secret",  # nosec B105 - field name mapping, not actual secret
        "SHOPWARE_GRANT_TYPE": "grant_type",
        "SHOPWARE_STORE_API_SW_ACCESS_KEY": "store_api_sw_access_key",
        "SHOPWARE_INSECURE_TRANSPORT": "insecure_transport",
    }
    env_values: dict[str, Any] = {}
    for env_key, field_name in env_mapping.items():
        value = os.environ.get(env_key)
        if value is not None:
            env_values[field_name] = value
    return env_values


def _find_env_file(filename: str = ".env") -> Path | None:
    """
    Search for an env file in current directory and parent directories.

    Args:
        filename: Name of the env file to search for (default: ".env")

    Returns:
        Path to the found env file, or None if not found
    """
    current = Path.cwd().resolve()
    root = Path(current.anchor)

    while current != root:
        env_path = current / filename
        if env_path.exists():
            return env_path
        current = current.parent

    # Check root directory as well
    env_path = root / filename
    if env_path.exists():
        return env_path

    return None


def load_config_from_env(env_file: str | Path | None = None) -> ConfShopware6ApiBase:
    """
    Load configuration from a .env file.

    Args:
        env_file: Path to the .env file. If None, searches for .env in:
                  1. Current working directory
                  2. Parent directories (up to filesystem root)
                  3. Falls back to environment variables only

    Returns:
        ConfShopware6ApiBase: Loaded configuration object

    Raises:
        ConfigurationError: If the specified env_file does not exist

    Example:
        >>> my_config = load_config_from_env()  # Auto-find .env in cwd or parents
        >>> my_config = load_config_from_env("/path/to/my.env")  # Load from specific file

    """
    if env_file is not None:
        return ConfShopware6ApiBase.from_env_file(env_file)

    # Search for .env in current directory and parent directories
    found_env = _find_env_file()
    if found_env is not None:
        return ConfShopware6ApiBase.from_env_file(found_env)

    # No .env file found - load from environment variables only
    # This is valid if user has set env vars directly
    return ConfShopware6ApiBase.from_env_vars()


def require_config_from_env(env_file: str | Path | None = None) -> ConfShopware6ApiBase:
    """
    Load configuration from a .env file, requiring it to exist.

    Unlike load_config_from_env(), this function raises an error if no .env
    file is found.

    Args:
        env_file: Path to the .env file. If None, searches for .env in
                  current directory and parent directories.

    Returns:
        ConfShopware6ApiBase: Loaded configuration object

    Raises:
        ConfigurationError: If no .env file is found

    """
    if env_file is not None:
        env_path = Path(env_file)
        if not env_path.exists():
            raise ConfigurationError(
                f"Configuration file not found: {env_path}\n\n"
                f"This application requires a .env file with Shopware 6 API credentials.\n"
                f"See 'example.env' in the project root for a documented template:\n"
                f"  https://github.com/bitranox/lib_shopware6_api_base/blob/master/example.env\n\n"
                f"Quick start:\n"
                f"  1. Copy example.env to {env_path.name}\n"
                f"  2. Edit {env_path.name} with your shop's credentials\n"
            )
        return ConfShopware6ApiBase.from_env_file(env_path)

    # Search for .env in current directory and parent directories
    found_env = _find_env_file()
    if found_env is None:
        raise ConfigurationError(
            "Configuration file not found: .env\n\n"
            "Searched in current directory and all parent directories.\n"
            "This application requires a .env file with Shopware 6 API credentials.\n"
            "See 'example.env' in the project root for a documented template:\n"
            "  https://github.com/bitranox/lib_shopware6_api_base/blob/master/example.env\n\n"
            "Quick start:\n"
            "  1. Copy example.env to .env in your project root\n"
            "  2. Edit .env with your shop's credentials\n"
        )

    return ConfShopware6ApiBase.from_env_file(found_env)
